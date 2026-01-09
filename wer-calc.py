import csv
import re

def load_csv(path):
    data = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for idx, sentence in reader:
            # sentence = re.sub("[^a-zA-Z ]", "", sentence)
            data[idx] = sentence.strip().upper()
    return data

def wer(ref, hyp):
    r = ref.split()
    h = hyp.split()

    dp = [[0] * (len(h) + 1) for _ in range(len(r) + 1)]

    for i in range(len(r) + 1):
        dp[i][0] = i
    for j in range(len(h) + 1):
        dp[0][j] = j

    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            if r[i - 1] == h[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = min(
                    dp[i - 1][j] + 1,    # deletion
                    dp[i][j - 1] + 1,    # insertion
                    dp[i - 1][j - 1] + 1 # substitution
                )

    return dp[-1][-1] / max(1, len(r))

def cer(ref, hyp):
    # standard: remove spaces
    r = list(ref.replace(" ", ""))
    h = list(hyp.replace(" ", ""))

    dp = [[0] * (len(h) + 1) for _ in range(len(r) + 1)]

    for i in range(len(r) + 1):
        dp[i][0] = i
    for j in range(len(h) + 1):
        dp[0][j] = j

    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            if r[i - 1] == h[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = min(
                    dp[i - 1][j] + 1,    # deletion
                    dp[i][j - 1] + 1,    # insertion
                    dp[i - 1][j - 1] + 1 # substitution
                )

    return dp[-1][-1] / max(1, len(r))

def evaluate_run_cer(gt, preds):
    cers = []
    for idx in gt:
        if idx not in preds:
            continue
        cers.append(cer(gt[idx], preds[idx]))
    return sum(cers) / len(cers)


def evaluate_run(gt, preds):
    wers = []
    for idx in gt:
        if idx not in preds:
            continue
        wers.append(wer(gt[idx], preds[idx]))
    return sum(wers) / len(wers)

gt = load_csv("labels.csv")

preds = {
    "feli": load_csv("sentences-feli/hypos-feli.txt"),
    "jannis": load_csv("sentences-jannis/hypos-jannis.txt"),
    "richard": load_csv("sentences-richard/hypos-richard.txt")
}
WER=0
CER=0
for i, pred in preds.items():
    _wer = evaluate_run(gt, pred)
    _cer = evaluate_run_cer(gt, pred)
    print(
        f"Run {i}: "
        f"WER={_wer:.4f}, "
        f"CER={_cer:.4f}"
    )
    WER+=_wer
    CER+=_cer
WER /= 3
CER /= 3
print(f"AVG: {WER=:.4f}, {CER=:.4f}")