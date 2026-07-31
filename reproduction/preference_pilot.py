import hashlib
import json
import math
import re
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np


DATASET = "princeton-nlp/llama3-ultrafeedback-armorm"
DATASET_REVISION = "9d189bae5856a823f3708d2c2bc4dbb43c90eb11"
OFFSETS = (0, 7484, 14968, 22452, 29936, 37420, 44904, 52388)
ROWS_PER_OFFSET = 64
USER_AGENT = "ICMLPapers-reproduction/1.0"


def fetch_json(url):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def current_dataset_revision():
    metadata = fetch_json(f"https://huggingface.co/api/datasets/{DATASET}")
    return metadata["sha"]


def fetch_pairs():
    if current_dataset_revision() != DATASET_REVISION:
        raise RuntimeError("Pinned dataset revision is no longer current; refusing viewer rows")
    pairs = []
    for offset in OFFSETS:
        query = urllib.parse.urlencode(
            {
                "dataset": DATASET,
                "config": "default",
                "split": "train",
                "offset": offset,
                "length": ROWS_PER_OFFSET,
            }
        )
        page = fetch_json(f"https://datasets-server.huggingface.co/rows?{query}")
        for item in page["rows"]:
            row = item["row"]
            pairs.append(
                {
                    "row_idx": item["row_idx"],
                    "chosen": row["chosen"][-1]["content"],
                    "rejected": row["rejected"][-1]["content"],
                }
            )
    if current_dataset_revision() != DATASET_REVISION:
        raise RuntimeError("Dataset revision changed during row retrieval")
    if len(pairs) != len(OFFSETS) * ROWS_PER_OFFSET:
        raise RuntimeError(f"Expected 512 pairs, received {len(pairs)}")
    return pairs


def subset_sha256(pairs):
    payload = json.dumps(pairs, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()


def response_features(text, dimensions=512, max_tokens=256):
    tokens = re.findall(r"[a-z0-9']+", text.lower())[:max_tokens]
    features = np.zeros(dimensions, dtype=np.float64)
    terms = tokens + [f"{left}\u241f{right}" for left, right in zip(tokens, tokens[1:])]
    for term in terms:
        digest = hashlib.blake2b(term.encode(), digest_size=8).digest()
        value = int.from_bytes(digest, "little")
        index = value % dimensions
        features[index] += 1.0 if value & (1 << 63) else -1.0
    norm = np.linalg.norm(features)
    return features / norm if norm else features


def pair_matrix(pairs):
    rows = [
        response_features(pair["chosen"]) - response_features(pair["rejected"])
        for pair in pairs
    ]
    return np.stack(rows)


def sigmoid(values):
    return 1.0 / (1.0 + np.exp(-np.clip(values, -60.0, 60.0)))


def logistic_loss(logits):
    return float(np.mean(np.logaddexp(0.0, -logits)))


def train_reference(matrix, seed, corruption_rate, epochs, learning_rate, l2):
    rng = np.random.default_rng(seed)
    labels = np.ones(len(matrix))
    flipped = rng.choice(len(matrix), size=round(corruption_rate * len(matrix)), replace=False)
    labels[flipped] = -1.0
    weights = np.zeros(matrix.shape[1])
    for _ in range(epochs):
        signed_logits = labels * (matrix @ weights)
        gradient = -(matrix.T @ (labels * sigmoid(-signed_logits))) / len(matrix) + l2 * weights
        weights -= learning_rate * gradient
    return weights


def train_policy(matrix, reference_weights, beta, margin, epochs, learning_rate, l2):
    weights = reference_weights.copy()
    delta_ref = matrix @ reference_weights
    losses = []
    undesirable = []
    for _ in range(epochs):
        delta = matrix @ weights
        logits = beta * (delta - delta_ref) - margin
        losses.append(logistic_loss(logits))
        undesirable.append(float(np.mean((delta < 0.0) & (delta > delta_ref))))
        gradient = matrix.T @ (-beta * sigmoid(-logits)) / len(matrix)
        gradient += l2 * (weights - reference_weights)
        weights -= learning_rate * gradient
    final_logits = beta * (matrix @ weights - delta_ref) - margin
    losses.append(logistic_loss(final_logits))
    return weights, losses, undesirable


def evaluate(test_matrix, reference_weights, policy_weights):
    delta_ref = test_matrix @ reference_weights
    delta = test_matrix @ policy_weights
    misaligned = delta_ref <= 0.0
    escape_rate = float(np.mean(delta[misaligned] > 0.0)) if np.any(misaligned) else 1.0
    return {
        "reference_accuracy": float(np.mean(delta_ref > 0.0)),
        "policy_accuracy": float(np.mean(delta > 0.0)),
        "undesirable_fraction": float(np.mean((delta < 0.0) & (delta > delta_ref))),
        "escape_rate": escape_rate,
        "mean_delta_ref": float(np.mean(delta_ref)),
        "mean_delta": float(np.mean(delta)),
    }


def run_preference_pilot(protocol_path):
    protocol = json.loads(Path(protocol_path).read_text())
    pairs = fetch_pairs()
    matrix = pair_matrix(pairs)
    train_matrix = matrix[: 6 * ROWS_PER_OFFSET]
    test_matrix = matrix[6 * ROWS_PER_OFFSET :]
    results = []
    gamma_zero_control = True

    for seed in protocol["seeds"]:
        for corruption_rate in protocol["label_corruption_rates"]:
            reference = train_reference(
                train_matrix,
                seed,
                corruption_rate,
                protocol["reference_epochs"],
                protocol["learning_rate"],
                protocol["l2"],
            )
            delta_ref_train = train_matrix @ reference
            reference_probability = sigmoid(delta_ref_train)
            cpo_margin = protocol["gamma"] * (
                1.0 / reference_probability + 1.0 / (1.0 - reference_probability)
            )
            dpo, dpo_losses, dpo_undesirable = train_policy(
                train_matrix,
                reference,
                protocol["beta"],
                np.zeros(len(train_matrix)),
                protocol["policy_epochs"],
                protocol["learning_rate"],
                protocol["l2"],
            )
            cpo, cpo_losses, cpo_undesirable = train_policy(
                train_matrix,
                reference,
                protocol["beta"],
                cpo_margin,
                protocol["policy_epochs"],
                protocol["learning_rate"],
                protocol["l2"],
            )
            dpo_control, control_losses, _ = train_policy(
                train_matrix,
                reference,
                protocol["beta"],
                np.zeros(len(train_matrix)),
                protocol["policy_epochs"],
                protocol["learning_rate"],
                protocol["l2"],
            )
            gamma_zero_control &= np.array_equal(dpo, dpo_control) and dpo_losses == control_losses
            results.append(
                {
                    "seed": seed,
                    "corruption_rate": corruption_rate,
                    "dpo": {
                        **evaluate(test_matrix, reference, dpo),
                        "initial_train_loss": dpo_losses[0],
                        "final_train_loss": dpo_losses[-1],
                        "max_train_undesirable_fraction": max(dpo_undesirable),
                    },
                    "cpo": {
                        **evaluate(test_matrix, reference, cpo),
                        "initial_train_loss": cpo_losses[0],
                        "final_train_loss": cpo_losses[-1],
                        "max_train_undesirable_fraction": max(cpo_undesirable),
                        "mean_margin": float(np.mean(cpo_margin)),
                    },
                }
            )

    mean_dpo_escape = float(np.mean([result["dpo"]["escape_rate"] for result in results]))
    mean_cpo_escape = float(np.mean([result["cpo"]["escape_rate"] for result in results]))
    mean_dpo_accuracy = float(np.mean([result["dpo"]["policy_accuracy"] for result in results]))
    mean_cpo_accuracy = float(np.mean([result["cpo"]["policy_accuracy"] for result in results]))
    gates = {
        "C2": all(
            result["dpo"]["final_train_loss"] < result["dpo"]["initial_train_loss"]
            for result in results
        )
        and any(result["dpo"]["reference_accuracy"] < 0.5 for result in results),
        "C3": any(
            result["dpo"]["max_train_undesirable_fraction"] > 0.0
            and result["dpo"]["final_train_loss"] < result["dpo"]["initial_train_loss"]
            for result in results
        ),
        "C4": mean_cpo_escape >= mean_dpo_escape + 0.02
        and mean_cpo_accuracy >= mean_dpo_accuracy
        and gamma_zero_control,
    }
    return {
        "dataset": DATASET,
        "dataset_revision": DATASET_REVISION,
        "subset_sha256": subset_sha256(pairs),
        "train_rows": len(train_matrix),
        "test_rows": len(test_matrix),
        "feature_dimensions": matrix.shape[1],
        "gates": gates,
        "gamma_zero_control": gamma_zero_control,
        "aggregate": {
            "mean_dpo_escape_rate": mean_dpo_escape,
            "mean_cpo_escape_rate": mean_cpo_escape,
            "mean_dpo_accuracy": mean_dpo_accuracy,
            "mean_cpo_accuracy": mean_cpo_accuracy,
        },
        "runs": results,
    }
