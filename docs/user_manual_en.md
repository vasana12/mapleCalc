# 📘 User Manual — Mapulator

Mapulator is a GUI-based tool designed for advanced MapleStory players seeking to optimize item farming efficiency through **statistical drop rate simulation** and **real-time hunt rate measurement**.

---

## 🧩 Features

### 1. Drop Probability Estimation
- Calculate how many monsters you need to hunt to reach a **target item drop count**
- Supports statistical thresholds: 50%, 60%, 70%, 80%, 90%, 99%

### 2. Real-Time Hunt Rate Measurement
- Measure kills per minute by logging EXP before and after a given time window
- Project total hunt time needed to meet item farming goals with real-world accuracy

### 3. Configurable Monster Data
- Save monster name, item name, drop rate (as `%` or decimal), and EXP per kill
- Automatically persisted in `drop_configs.json`

---

## 🛠 How to Use

### 1️⃣ Save Configuration
1. Open the **“Save Config”** tab
2. Enter:
   - Monster Name
   - Item Name
   - Drop Rate (`50%` or `0.5`)
   - EXP per kill
3. Press `Enter` or click 💾 Save  
→ Configuration is saved locally and available across all tabs.

### 2️⃣ Estimate Drops
1. Go to the **“Drop Estimation”** tab
2. Select saved config and input your target drop count
3. Press `Enter` or click 🔍 Estimate  
→ It calculates how many monsters you need to kill for various confidence levels.

### 3️⃣ Measure Time
1. Go to the **“Time Estimation”** tab
2. Choose config and enter target drop count (optional)
3. Enter starting EXP → click ▶ Start Timer
4. After `n` minutes or manual stop, input ending EXP
5. Click ⏳ Estimate  
→ You’ll get: required kills, hunt rate, and estimated time.

---

## 🧪 Example Output
Required kills (90%): 731
Kill rate: 22.15 kills/min
Estimated time: 33.0 minutes


---

## 💡 Tips

- You can press `Enter` to quickly trigger Save or Estimate actions.
- If EXP gain is `0`, you’ll be warned.
- Default target count is `1` if left empty.

---

## 📬
- GitHub: vasana12@naver.com
- Email: wodud6349@gmail.com