# 🧮 Income Tax Comparator (Old vs. New Regime)

A simple and efficient Streamlit app to compare your income tax liability under the **Old Regime vs. New Regime** for AY 2024–25 and 2025–26. Ideal for salaried employees, senior citizens, and anyone seeking clarity on India's tax system.

---

## 🚀 Features

- 📊 **Compare taxes** under Old and New Regimes
- 🧓 **Senior citizen support** (auto-includes 80TTB, enhanced 80D limits)
- 💸 Input major deductions:
  - Section 80C (LIC, PPF, ELSS, etc.)
  - Section 80D (Health Insurance)
  - HRA Exemption
  - Home Loan Interest (24b)
  - Other sections (80E, 80G, etc.)
- 🧾 **Auto-applies** standard deduction and 87A rebate
- 📄 **Downloadable PDF report**
- 🧮 Transparent breakdown of tax slabs & cess

---

## 🖥️ Demo (if hosted)

[🔗 View Live App](https://tax-regime-simulator.streamlit.app/) *(replace with actual URL after deployment)*

---

## 📦 Requirements

- Python 3.8+
- Streamlit
- fpdf

---

## 📁 Installation & Running Locally

1. **Clone the repo**
```bash
git clone https://github.com/yourusername/tax-comparator.git
cd tax-comparator
```


2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. Run the App
```bash 
streamlit run tax-simulator.py
```

Visit http://localhost:8501 in your browser.

## 🗂️ File Structure

tax-comparator/

├── tax_comparator.py        # Main Streamlit app

├── requirements.txt         # Dependency file

└── README.md                # Project documentation

### 🤝 Contributing
Pull requests are welcome! Please open an issue first to discuss what you would like to change or add.

### 📌 Disclaimer
This is a rough estimation tool. Always consult the official Income Tax portal or a certified Chartered Accountant for final tax filing.
