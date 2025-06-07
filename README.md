# CS291A Model Training Scripts

This repository contains training scripts for models used in our CS291A project, including fine-tuning and reinforcement learning (RL) setups with Qwen models and integration with PatchPilot.

---

## 🛠️ Setup Instructions

### 1. Create the Conda environment

```bash
conda env create -f environment.yaml
```

### 2. Activate the environment

```bash
conda activate verl
```

### 3. Navigate to the training directory

```bash
cd CS291A
```

---

## 🚀 Running Training Scripts

This repository includes `.sh` scripts for training models under different configurations.

For example, to train a reinforcement learning model using `Qwen/Qwen2.5-Coder-0.5B-Instruct` on file-level tasks (after fine-tuning), run:

```bash
bash train_model_0.5_file_level_finetuned.sh
```

Explore the `.sh` files in the directory for additional training setups.

---

## 🤖 Using PatchPilot with Our Models

To run PatchPilot with our trained models:

1. Clone the PatchPilot repository:

   [https://github.com/ucsb-mlsec/PatchPilot.git](https://github.com/ucsb-mlsec/PatchPilot.git)

2. Follow their instructions to run inference using our models.

---

## 📦 Our Models

All trained models are available at:

👉 [https://huggingface.co/CS291A](https://huggingface.co/CS291A)

---

## 📄 License

This project is for academic and research use only. See the LICENSE file for details.

---

## ✉️ Contact

For questions or issues, please open an issue or reach out via course communication channels.
