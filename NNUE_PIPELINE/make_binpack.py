#!/usr/bin/env python3
import sys, os, struct
import numpy as np
import chess

MAGIC = b"BINPACK\x00"

# ---- Match model/features/halfka_v2_hm.py ----
NUM_SQ = 64
NUM_PT_REAL = 11
NUM_PT_VIRTUAL = 12

NUM_PLANES_REAL = NUM_SQ * NUM_PT_REAL      # 704
NUM_PLANES_VIRTUAL = NUM_SQ * NUM_PT_VIRTUAL # 768

NUM_REAL = NUM_PLANES_REAL * NUM_SQ // 2    # 22528
NUM_VIRT = NUM_PLANES_VIRTUAL               # 768
FEAT_N = NUM_REAL + NUM_VIRT                # 23296

# fmt: off (copied from your halfka_v2_hm.py)
KingBuckets = [
  -1, -1, -1, -1, 31, 30, 29, 28,
  -1, -1, -1, -1, 27, 26, 25, 24,
  -1, -1, -1, -1, 23, 22, 21, 20,
  -1, -1, -1, -1, 19, 18, 17, 16,
  -1, -1, -1, -1, 15, 14, 13, 12,
  -1, -1, -1, -1, 11, 10, 9, 8,
  -1, -1, -1, -1, 7, 6, 5, 4,
  -1, -1, -1, -1, 3, 2, 1, 0
]
# fmt: on

def orient(is_white_pov: bool, sq: int, ksq: int) -> int:
    # ksq must not be oriented
    kfile = ksq % 8
    return (7 * (kfile < 4)) ^ (56 * (not is_white_pov)) ^ sq

def halfka_idx(is_white_pov: bool, king_sq: int, sq: int, p: chess.Piece) -> int:
    # p_idx in [0..11], then one king plane removed -> [0..10] effectively
    p_idx = (p.piece_type - 1) * 2 + (p.color != is_white_pov)
    o_ksq = orient(is_white_pov, king_sq, king_sq)
    if p_idx == 11:
        p_idx -= 1
    kb = KingBuckets[o_ksq]
    if kb < 0:
        return None
    return (
        orient(is_white_pov, sq, king_sq)
        + p_idx * NUM_SQ
        + kb * NUM_PLANES_REAL
    )

def factor_A_index(real_idx: int) -> int:
    # Matches FactorizedFeatures.get_feature_factors() in your file
    a_idx = real_idx % NUM_PLANES_REAL
    k_idx = real_idx // NUM_PLANES_REAL

    # Special adjustment for "virtual king plane" behavior
    # if a_idx plane == 10 (i.e., a_idx//64 == 10) and king bucket differs
    if (a_idx // NUM_SQ) == 10 and k_idx != KingBuckets[a_idx % NUM_SQ]:
        a_idx += NUM_SQ

    if not (0 <= a_idx < NUM_PLANES_VIRTUAL):
        return None
    return NUM_REAL + a_idx  # virtual features appended after real

def encode_halfkav2_hm_factorized(board: chess.Board):
    """
    Returns uint8 dense vector length 23296.
    Activates:
      - real HalfKAv2_hm feature indices (22528)
      - corresponding factor "A" virtual indices (768) for each real feature
    POV = side to move (matches training).
    """
    pov_white = board.turn
    ksq = board.king(pov_white)
    if ksq is None:
        return None

    x = np.zeros(FEAT_N, dtype=np.uint8)

    # Iterate all pieces on board (including kings; halfka_idx handles the removed plane)
    for sq, p in board.piece_map().items():
        ridx = halfka_idx(pov_white, ksq, sq, p)
        if ridx is None:
            continue
        if 0 <= ridx < NUM_REAL:
            x[ridx] = 1
            vidx = factor_A_index(ridx)
            if vidx is not None:
                x[vidx] = 1

    return x

def parse_line_to_board_and_eval(line):
    # Expect: "<FEN 6 fields> <cp_eval>"
    parts = line.strip().split()
    if len(parts) < 7:
        return None
    fen = " ".join(parts[:6])
    try:
        raw_eval_cp = float(parts[-1])
    except:
        return None
    try:
        b = chess.Board(fen)
    except:
        return None
    return b, (raw_eval_cp / 100.0)  # pawns

def convert_fen_to_binpack(in_path, out_path):
    # count valid samples
    n = 0
    with open(in_path) as f:
        for ln in f:
            parsed = parse_line_to_board_and_eval(ln)
            if not parsed:
                continue
            b, _ = parsed
            feats = encode_halfkav2_hm_factorized(b)
            if feats is not None:
                n += 1

    if n == 0:
        print("No valid positions found.")
        return

    with open(out_path, "wb") as out, open(in_path) as f:
        out.write(MAGIC)
        out.write(struct.pack("<i", FEAT_N))
        out.write(struct.pack("<q", n))

        wrote = 0
        for ln in f:
            parsed = parse_line_to_board_and_eval(ln)
            if not parsed:
                continue
            b, t = parsed
            feats = encode_halfkav2_hm_factorized(b)
            if feats is None:
                continue
            out.write(feats.tobytes(order="C"))
            out.write(struct.pack("<f", float(t)))
            wrote += 1

        assert wrote == n, (wrote, n)

    print(f"Wrote {n} HalfKAv2_hm^ positions to {out_path}")
    print(f"Header: magic={MAGIC} feat_n={FEAT_N} count={n}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python make_binpack.py <input_fen+evals.txt> <output.binpack>")
        sys.exit(1)
    inp, outp = sys.argv[1], sys.argv[2]
    if not os.path.exists(inp):
        print(f"Input missing: {inp}")
        sys.exit(1)
    convert_fen_to_binpack(inp, outp)
