import streamlit as st
from fpdf import FPDF
import tempfile
from datetime import datetime

# Streamlit UI Setup
st.set_page_config(page_title="Tax Regime Comparator", layout="centered")

st.title("📟 Income Tax Comparator")

# Assessment Year toggle
assessment_year = st.selectbox("Assessment Year", options=["2024–25", "2025–26"], index=1)

# Senior Citizen Toggle
is_senior = st.toggle("Are you a Senior Citizen (60ers or older)?", value=False)

# Section 80TTB if Senior
ded_80ttb = 0
if is_senior:
    ded_80ttb = st.number_input("🏦 Section 80TTB (Interest Income Deduction) [Max: ₹50,000]", min_value=0, max_value=50000, step=1000, format="%i", key="ded_80ttb")
    if ded_80ttb >= 50000:
        st.caption("✅ You've reached the maximum 80TTB deduction (₹50,000).")

# Session state for reset
def reset_fields():
    fields_to_clear = [
        "salary_income", "rental_income", "ltcg", "stcg",
        "ded_80c", "ded_80d", "ded_hra", "ded_home_loan", "ded_other", "ded_80ttb"
    ]
    for key in fields_to_clear:
        if key in st.session_state:
            st.session_state[key] = 0

st.button("🔁 Clear All Fields", on_click=reset_fields)

# Income sources
st.markdown("### 💼 Income Details")
salary_income = st.number_input("👨‍💼 Salary Income (₹)", min_value=0, step=1000, format="%i", key="salary_income")

# Toggle for additional income
show_additional_income = st.toggle("Do you have additional income sources (rental, capital gains)?", value=False)
rental_income = ltcg = stcg = 0
if show_additional_income:
    rental_income = st.number_input("🏠 Rental Income (₹)", min_value=0, step=1000, format="%i", key="rental_income")
    ltcg = st.number_input("📈 Long-Term Capital Gains (LTCG) (₹)", min_value=0, step=1000, format="%i", key="ltcg")
    stcg = st.number_input("📉 Short-Term Capital Gains (STCG) (₹)", min_value=0, step=1000, format="%i", key="stcg")

income = salary_income + rental_income

st.markdown("### 💼 Deductions Under Old Regime")
ded_80c = st.number_input("📟 Section 80C (LIC, PPF, EPF etc.) [Max: ₹1,50,000]", min_value=0, max_value=150000, step=1000, format="%i", key="ded_80c")
if ded_80c >= 150000:
    st.caption("✅ You've reached the maximum limit for Section 80C (₹1,50,000).")

max_80d = 50000 if is_senior else 25000
ded_80d = st.number_input(f"🏥 Section 80D (Health Insurance Premium) [Max: ₹{max_80d:,}]", min_value=0, max_value=max_80d, step=1000, format="%i", key="ded_80d")
if ded_80d >= max_80d:
    st.caption(f"✅ Maximum deduction allowed under Section 80D is ₹{max_80d:,}.")

ded_hra = st.number_input("🏠 HRA Exemption (If known, override here) (₹)", min_value=0, step=1000, format="%i", key="ded_hra")
st.caption("ℹ️ If you know the HRA deduction amount (as per Form 16 or employer), enter it here directly.")

max_home_loan = 200000
ded_home_loan = st.number_input("🏡 Home Loan Interest (Section 24b) [Max: ₹2,00,000]", min_value=0, max_value=max_home_loan, step=1000, format="%i", key="ded_home_loan")
if ded_home_loan >= max_home_loan:
    st.caption("✅ ₹2,00,000 is the maximum allowed deduction under Section 24b.")

ded_other = st.number_input("📄 Other Deductions (80E, 80G, etc.)", min_value=0, step=1000, format="%i", key="ded_other")

deductions = ded_80c + ded_80d + ded_hra + ded_home_loan + ded_other + ded_80ttb

# Capital Gains Tax Calculation
def calculate_capital_gains_tax(ltcg, stcg):
    ltcg_exemption = 100000
    ltcg_tax = 0
    if ltcg > ltcg_exemption:
        ltcg_tax = (ltcg - ltcg_exemption) * 0.10
    stcg_tax = stcg * 0.15
    return round(ltcg_tax + stcg_tax)

# Tax calculation functions
def calculate_old_tax(income, deductions, senior):
    breakdown = []
    taxable = max(0, income - deductions)
    breakdown.append(("Taxable Income after deductions", taxable))
    tax = 0
    slab1 = 300000 if senior else 250000
    if taxable <= slab1:
        tax = 0
    elif taxable <= 500000:
        tax = (taxable - slab1) * 0.05
        breakdown.append((f"5% on income between {slab1//100000}L–5L", tax))
    elif taxable <= 1000000:
        tax = 12500 + (taxable - 500000) * 0.2
        breakdown.append(("20% on income between 5L–10L", (taxable - 500000) * 0.2))
    else:
        tax = 112500 + (taxable - 1000000) * 0.3
        breakdown.append(("30% on income above 10L", (taxable - 1000000) * 0.3))
    if taxable <= 500000:
        breakdown.append(("Section 87A Rebate", -12500))
        tax = max(0, tax - 12500)
    tax_with_cess = round(tax * 1.04)
    breakdown.append(("+ 4% Cess", round(tax * 0.04)))
    breakdown.append(("Total Tax (Old Regime)", tax_with_cess))
    return tax_with_cess, breakdown

def calculate_new_tax(income, year):
    breakdown = []
    std_deduction = 50000 if year == "2024–25" else 75000
    taxable = max(0, income - std_deduction)
    breakdown.append(("Standard Deduction", std_deduction))
    breakdown.append(("Taxable Income", taxable))
    tax = 0
    slabs = [
        (250000, 0.00),
        (250000, 0.05),
        (250000, 0.10),
        (250000, 0.15),
        (250000, 0.20),
        (float('inf'), 0.30),
    ] if year == "2024–25" else [
        (300000, 0.00),
        (300000, 0.05),
        (300000, 0.10),
        (300000, 0.15),
        (300000, 0.20),
        (300000, 0.25),
        (float('inf'), 0.30),
    ]
    remaining = taxable
    for slab, rate in slabs:
        if remaining <= 0:
            break
        slab_amount = min(remaining, slab)
        portion = slab_amount * rate
        if rate > 0:
            breakdown.append((f"{int(rate * 100)}% on ₹{int(slab_amount):,}", round(portion)))
        tax += portion
        remaining -= slab_amount
    rebate_limit = 500000 if year == "2024–25" else 700000
    if income <= rebate_limit:
        breakdown.append(("Section 87A Rebate", -int(tax)))
        tax = 0
    tax_with_cess = round(tax * 1.04)
    breakdown.append(("+ 4% Cess", round(tax * 0.04)))
    breakdown.append(("Total Tax (New Regime)", tax_with_cess))
    return tax_with_cess, breakdown

def breakdown_log(breakdown):
    for label, value in breakdown:
        st.write(f"- {label}: ₹{value:,}")

# PDF generator
def generate_pdf_report(income, old_tax, new_tax, savings):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Income Tax Comparison Report", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Gross Income: Rs.{income:,}", ln=True)
    pdf.cell(200, 10, txt=f"Old Regime Tax: Rs.{old_tax:,}", ln=True)
    pdf.cell(200, 10, txt=f"New Regime Tax: Rs.{new_tax:,}", ln=True)
    pdf.cell(200, 10, txt=f"You save Rs.{savings:,} using {'New' if savings > 0 else 'Old'} Regime.", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", size=10)
    disclaimer = ("Disclaimer: This report is a rough estimate based on provided data. "
                  "Please cross-verify with the official Income Tax portal or your Chartered Accountant.")
    pdf.multi_cell(0, 10, txt=disclaimer.encode("latin-1", "ignore").decode("latin-1"))
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)
    return temp_file.name

# Main logic
if income > 0:
    old_tax, old_breakdown = calculate_old_tax(income, deductions, is_senior)
    new_tax, new_breakdown = calculate_new_tax(income, assessment_year)
    cap_gains_tax = calculate_capital_gains_tax(ltcg, stcg)
    savings = old_tax - new_tax

    st.markdown("### 💰 Tax Comparison")
    st.success(f"Old Regime Tax: ₹{old_tax:,}")
    st.success(f"New Regime Tax: ₹{new_tax:,}")
    st.info(f"📊 Capital Gains Tax (LTCG+STCG): ₹{cap_gains_tax:,}")

    if savings > 0:
        st.info(f"🎯 You save ₹{savings:,} by opting for the **New Regime**")
    elif savings < 0:
        st.info(f"💡 You save ₹{abs(savings):,} by staying in the **Old Regime**")
    else:
        st.warning("Both regimes result in the same tax liability.")

    st.markdown("#### 📊 Breakdown - Old Regime")
    breakdown_log(old_breakdown)
    st.markdown("#### 📊 Breakdown - New Regime")
    breakdown_log(new_breakdown)

    pdf_path = generate_pdf_report(income, old_tax, new_tax, savings)
    with open(pdf_path, "rb") as f:
        st.download_button("📄 Download Tax Report (PDF)", f, file_name="Tax_Comparison_Report.pdf", mime="application/pdf")

    st.markdown("---")
    st.markdown("⚠️ **Disclaimer:** The calculations are a rough estimate. Please verify with your own tax documents or consult a financial expert.")
