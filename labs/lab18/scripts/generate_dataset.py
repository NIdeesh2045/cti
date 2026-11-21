
import csv
import json
import random
import hashlib
from pathlib import Path
from datetime import datetime, timedelta, timezone

random.seed(42)

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SOURCES = [
    "BleepingComputer", "CISA Advisories", "CISA KEV",
    "Cisco Talos", "Curated sample", "Dark Reading",
    "Krebs on Security", "Microsoft Security Blog",
    "Rapid7 Blog", "SANS ISC", "Schneier on Security",
    "Securelist (Kaspersky)", "SecurityWeek",
    "The Hacker News", "Unit 42",
    "Synthetic Threat Feed"
]

THREAT_TYPES = [
    "DDoS", "Data Breach", "Malware", "Other",
    "Phishing", "Ransomware", "Vulnerability"
]

SEVERITIES = ["Low", "Medium", "High"]
STATUSES = ["New", "Investigating", "Mitigated", "Active"]

TARGETS = [
    "Healthcare", "Finance", "Government", "Education",
    "Technology", "Retail", "Energy", "Telecommunications"
]

TECHNIQUES = [
    "Phishing", "Credential Access", "Exploitation",
    "Command and Control", "Data Exfiltration",
    "Denial of Service", "Privilege Escalation"
]

CAMPAIGN_FAMILIES = [
    "malware", "phishing", "ransomware", "credential_theft",
    "data_exfiltration", "vulnerability", "botnet", "espionage"
]

TOTAL_RECORDS = 100_000
RECORDS_PER_CAMPAIGN = 10

start_date = datetime(2025, 1, 1, tzinfo=timezone.utc)

jsonl_path = OUTPUT_DIR / "threats_100k.jsonl"
csv_path = OUTPUT_DIR / "threats_100k.csv"

fields = [
    "threat_id", "title", "summary", "source",
    "type", "severity", "status", "target",
    "technique", "published_at", "iocs",
    "campaign_id", "campaign_family", "is_synthetic"
]

with jsonl_path.open("w", encoding="utf-8") as json_file, \
     csv_path.open("w", newline="", encoding="utf-8") as csv_file:

    writer = csv.DictWriter(csv_file, fieldnames=fields)
    writer.writeheader()

    for index in range(TOTAL_RECORDS):

        threat_number = index + 1
        campaign_number = index // RECORDS_PER_CAMPAIGN

        campaign_family = CAMPAIGN_FAMILIES[
            campaign_number % len(CAMPAIGN_FAMILIES)
        ]

        # One unique campaign for every group of 10 threats.
        campaign_id = f"campaign-{campaign_number:06d}"

        # Shared synthetic indicator within each campaign.
        ioc_value = hashlib.sha256(
            campaign_id.encode("utf-8")
        ).hexdigest()

        published_at = start_date + timedelta(
            minutes=random.randint(0, 1_000_000)
        )

        record = {
            "threat_id": f"THREAT-{threat_number:06d}",
            "title": f"Synthetic {random.choice(THREAT_TYPES)} Incident {threat_number}",
            "summary": (
                f"Synthetic security incident involving "
                f"{random.choice(TARGETS)}."
            ),
            "source": random.choice(SOURCES),
            "type": random.choice(THREAT_TYPES),
            "severity": random.choice(SEVERITIES),
            "status": random.choice(STATUSES),
            "target": random.choice(TARGETS),
            "technique": random.choice(TECHNIQUES),
            "published_at": published_at.isoformat(),
            "iocs": [
                f"synthetic-hash:{ioc_value}",
                f"synthetic-campaign:{campaign_id}"
            ],
            "campaign_id": campaign_id,
            "campaign_family": campaign_family,
            "is_synthetic": True
        }

        json_file.write(
            json.dumps(record) + "\n"
        )

        writer.writerow({
            **record,
            "iocs": json.dumps(record["iocs"])
        })

print("Synthetic dataset generated successfully!")
print(f"Total records: {TOTAL_RECORDS}")
print(f"Unique campaigns: {TOTAL_RECORDS // RECORDS_PER_CAMPAIGN}")
print(f"Records per campaign: {RECORDS_PER_CAMPAIGN}")
print(f"JSONL: {jsonl_path}")
print(f"CSV: {csv_path}")
print("All records are synthetic.")
