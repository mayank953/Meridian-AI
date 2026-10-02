"""Creates four small FICTIONAL PDFs about Aldermoor Industries for demos and tests.

Run from the project root:   python course/sample_docs/generate_sample_docs.py
Needs: pip install reportlab   (included in requirements-dev.txt)

Each document contains the answer to one of the example questions in the UI's
"Ask a question" tab, so the live demo gives the same result every time.
All numbers are made up for teaching. They are not legal, tax or accounting advice.
"""
import os

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
styles = getSampleStyleSheet()

DOCS = {
    "aldermoor_annual_report_fy2024.pdf": [
        ("Aldermoor Industries - Annual Report FY2024 (fictional)", None),
        ("Company overview", "Aldermoor Industries is a fictional German manufacturer of industrial packaging and filling machinery, headquartered in Hamburg, Germany. The company operates 40 subsidiaries in 28 countries and employs about 14,500 people."),
        ("Financial highlights", "Total revenue in FY2024 was EUR 2.84 billion, up from EUR 2.61 billion in FY2023 (an increase of 8.8 percent). Revenue in FY2022 was EUR 2.37 billion. EBITDA in FY2024 was EUR 398 million. Cost of goods sold (COGS) in FY2024 was EUR 1.92 billion."),
        ("Where we operate", "Aldermoor has manufacturing plants in Germany, Poland, China, Brazil and the United States. Sales and service offices are located in 28 countries across Europe, Asia, the Americas and Africa."),
        ("Workforce", "About 22 percent of the manufacturing workforce is expected to retire within the next five years. The company runs an apprenticeship programme with 450 apprentices."),
    ],
    "aldermoor_procurement_policy.pdf": [
        ("Aldermoor Industries - Procurement Policy (fictional)", None),
        ("Payment terms by vendor risk", "Vendors with a credit score of 75 or higher are low risk and receive standard Net-45 payment terms. This applies to servo motor suppliers, PLC suppliers and other strategic component suppliers. Vendors scoring 50 to 74 are moderate risk and require a 25 to 50 percent deposit or a confirmed letter of credit. Vendors scoring below 50 are high risk and require full prepayment plus a bank guarantee, or must be rejected."),
        ("Sanctions screening", "Every new vendor must be screened against EU, US OFAC, UN and German export-control lists before a purchase order is released. A sanctions match means immediate rejection."),
        ("Approval thresholds", "Purchases above EUR 250,000 need Department Head sign-off. Purchases above EUR 1,000,000 need CFO and Management Board approval."),
    ],
    "eu_tariff_schedule_excerpt.pdf": [
        ("EU Customs Tariff - Illustrative Excerpt (fictional teaching data)", None),
        ("Import duty rates", "Programmable controllers and PLC control units (tariff heading 8537 10) imported from Japan into the European Union: the customs duty rate is 2.2 percent of the customs value. Servo motors (heading 8501): 2.7 percent. Industrial sensors (heading 9031): 0 percent."),
        ("Import VAT", "Germany charges import VAT (Einfuhrumsatzsteuer) of 19 percent on the customs value plus duty. Intra-EU business-to-business supplies with a valid VAT ID are zero-rated under the reverse-charge mechanism."),
        ("Note", "These figures are illustrative teaching data and not legal or tax advice."),
    ],
    "aldermoor_accounting_policy_ifrs.pdf": [
        ("Aldermoor Industries - IFRS Accounting Policy (fictional)", None),
        ("Capitalisation", "Assets with a useful life of more than one year and a cost above EUR 5,000 are capitalised as property, plant and equipment under IAS 16. Smaller items and consumables are expensed immediately."),
        ("Depreciation schedule", "Filling line equipment is depreciated on a straight-line basis over 10 years. Production robots and tooling are depreciated over 8 years. IT hardware and servers are depreciated over 4 years. Buildings are depreciated over 30 years."),
        ("General ledger ranges", "Fixed assets use accounts 0xxx. Material costs use 5xxx. External services use 6xxx. Manufacturing overhead uses 4xxx."),
    ],
}

for filename, blocks in DOCS.items():
    doc = SimpleDocTemplate(os.path.join(OUT_DIR, filename), pagesize=A4, title=blocks[0][0])
    story = []
    for heading, body in blocks:
        if body is None:
            story += [Paragraph(heading, styles["Title"]), Spacer(1, 12)]
        else:
            story += [Paragraph(heading, styles["Heading2"]), Paragraph(body, styles["BodyText"]), Spacer(1, 10)]
    doc.build(story)
    print("created", filename)
