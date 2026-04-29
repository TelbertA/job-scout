def _job_row(job: dict) -> str:
    salary = "N/A"
    if job.get("job_min_salary") and job.get("job_max_salary"):
        salary = f"${int(job['job_min_salary']):,} - ${int(job['job_max_salary']):,}"

    skills_html = " ".join(
        f'<span class="badge">{s}</span>'
        for s in job.get("matched_skills", [])
        if not s.startswith("DISQUALIFIER")
    )

    return f"""
    <tr>
      <td><a href="{job.get('job_apply_link', '#')}" target="_blank">{job.get('job_title', '')}</a></td>
      <td>{job.get('employer_name', '')}</td>
      <td>{job.get('job_city', 'Remote') or 'Remote'}</td>
      <td><strong>{job['score']}</strong></td>
      <td>{salary}</td>
      <td>{skills_html}</td>
    </tr>"""

def generate_html(jobs: list[dict], date_str: str) -> str:
    rows = "".join(_job_row(j) for j in jobs)
    count = len(jobs)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Job Scout Report — {date_str}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; padding: 2rem; background: #0d1117; color: #c9d1d9; }}
    h1 {{ color: #58a6ff; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
    th {{ background: #161b22; padding: 0.75rem; text-align: left; border-bottom: 1px solid #30363d; }}
    td {{ padding: 0.65rem; border-bottom: 1px solid #21262d; vertical-align: top; }}
    a {{ color: #58a6ff; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .badge {{ background: #1f6feb; color: #fff; border-radius: 4px;
               padding: 2px 6px; font-size: 0.75rem; margin: 2px; display: inline-block; }}
    .meta {{ color: #8b949e; font-size: 0.9rem; margin-bottom: 1rem; }}
  </style>
</head>
<body>
  <h1>Job Scout Report</h1>
  <p class="meta">{date_str} &mdash; {count} qualified jobs (score &ge; 10)</p>
  <table>
    <thead>
      <tr>
        <th>Title</th><th>Company</th><th>Location</th>
        <th>Score</th><th>Salary</th><th>Matched Skills</th>
      </tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
</body>
</html>"""
