import os
import sys
import csv
import numpy as np
LOG_PATH = "./log"

def read_epoch_time(log_dir):
  experiments = os.listdir(log_dir)
  experiments.sort()
  print("========== Average epoch time(s) ==========")
  for e in experiments:
    exp_dir = os.path.join(log_dir, e)
    epoch_time = None

    # read the data of the first trainer
    log_path = os.path.join(exp_dir, "log_epoch_0.txt")
    if os.path.exists(log_path):
      try:
        with open(log_path, "r") as f:
          ret = f.readlines()[-1].strip().split()[-1]
        epoch_time = ret
        print("{}\t{}".format(e, epoch_time))
      except IndexError:
        print("{}\tN/A".format(e))

def read_itr_log(path):
  with open(path) as f:
    title = f.readline()
    title = title.strip().split('\t')
    reader = csv.reader(f, delimiter='\t')
    rows = [list(map(float, x)) for x in reader]
  return title, np.array(rows)

def diff_backward_time(log_dir):
  experiments = os.listdir(log_dir)
  experiments.sort()
  print("========== Difference of backward time / iteration time (s) ==========")
  for e in experiments:
    exp_dir = os.path.join(log_dir, e)
    num_trainers = len(os.listdir(exp_dir)) // 2
    data = []
    flag = False
    for i in range(num_trainers):
      itr_log = "log_itr_{}.txt".format(i)
      itr_log = os.path.join(exp_dir, itr_log)
      if not os.path.exists(itr_log):
        break
      title, rows = read_itr_log(itr_log)
      data.append(rows)
    data = np.array(data)
    if data.shape[0] < num_trainers or num_trainers <= 0:
      print("{}\t N/A".format(e))
      continue
    try:
      backward_idx = title.index('backward')
      itr_idx = title.index('itr')
      backward = data[:, :, backward_idx]
      itr_time = data[:, :, itr_idx]
      max_bw = np.max(backward, axis=0)
      min_bw = np.min(backward, axis=0)
      print("{}\t{:.4f}\t{:.4f}".format(e, np.mean(max_bw) - np.mean(min_bw), np.mean(itr_time))) # [trainer, iteration, field]
    except ValueError:
      print("{}\tN/A".format(e))

if __name__ == "__main__":
  if len(sys.argv) <= 1:
    dir_name = "latest"
  else:
    dir_name = sys.argv[1]
  log_dir = os.path.join(LOG_PATH, dir_name)
  read_epoch_time(log_dir)
  diff_backward_time(log_dir)