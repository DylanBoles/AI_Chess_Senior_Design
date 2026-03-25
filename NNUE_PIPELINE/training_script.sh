#python3 train.py \
#  /home/tun08104/senior_design/nnue-pytorch/Fischer_eval.binpack \
#  /home/tun08104/senior_design/nnue-pytorch/Fischer_eval.binpack \
#  --gpus "0," \
#  --threads 8 \
#  --num-workers 8 \
#  --batch-size 256 \
#  --random-fen-skipping 1 \
#  --features=HalfKAv2_hm^ \
#  --lambda=1.0 \
#  --epoch-size 250000 \
#  --max_epochs 10 \
#  --compile-backend none \
#  --default_root_dir /home/tun08104/senior_design/nnue_runs
#python /home/tun08104/senior_design/nnue-pytorch/train.py \
 # /home/tun08104/senior_design/nnue-pytorch/Fischer_eval.binpack \
  #--features HalfKAv2_hm \
  #--l1 3072 \
  #--gpus 0 \
  #--batch-size 512 \
  #--max_epochs 20 \
  #--epoch-size 23500 \
  #--validation-size 2000 \
  #--num-workers 0 \
  #--network-save-period 2 \
  #--compile-backend inductor \
  #--default_root_dir /home/tun08104/senior_design/nnue_runs
python /home/tun08104/senior_design/nnue-pytorch/train.py \
  /home/tun08104/senior_design/nnue-pytorch/Anand.binpack \
  --features HalfKAv2_hm \
  --l1 3072 \
  --gpus 0 \
  --batch-size 512 \
  --lr 0.005 \
  --max_epochs 20 \
  --epoch-size 500000 \
  --validation-size 20000 \
  --random-fen-skipping 1 \
  --num-workers 0 \
  --network-save-period 1 \
  --compile-backend inductor \
  --default_root_dir /home/tun08104/senior_design/nnue_runs
