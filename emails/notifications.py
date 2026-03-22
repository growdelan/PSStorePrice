"""Budowanie i wysylka powiadomien e-mail o obnizkach."""

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import html
import smtplib
import ssl


def build_plain_text_body(changes: list[dict]) -> str:
    """Buduje prosty fallback tekstowy."""
    if not changes:
        return "Brak zmian cen."

    lines = []
    for index, change in enumerate(changes, start=1):
        lines.append(
            f"{index}. {change['Nazwa']} | z {change['cena']:.2f} zl na "
            f"{change['przecena']:.2f} zl | {change['Link']}"
        )
    return "\n".join(lines)


def build_email_html(changes: list[dict]) -> str:
    """Buduje HTML wzorowany na obecnym workflow n8n."""
    if not changes:
        rows = "<tr><td class=\"content\"><div class=\"title\">Brak zmian cen.</div></td></tr>"
    else:
        rendered_rows = []
        for index, change in enumerate(changes, start=1):
            rendered_rows.append(
                f"""
                <tr>
                  <td class="idx">{index}.</td>
                  <td class="content">
                    <div class="title">
                      <a href="{html.escape(change['Link'], quote=True)}" target="_blank" rel="noopener">
                        {html.escape(change['Nazwa'])}
                      </a>
                    </div>
                    <div class="prices">
                      <span class="old">z {change['cena']:.2f} zl</span>
                      <span class="arrow">→</span>
                      <span class="new">{change['przecena']:.2f} zl</span>
                    </div>
                    <div class="link">{html.escape(change['Link'])}</div>
                  </td>
                </tr>
                """
            )
        rows = "".join(rendered_rows)

    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Zmiany cen ({len(changes)})</title>
<style>
  body{{font-family:Arial,Helvetica,sans-serif;margin:0;padding:24px;background:#f6f7fb;color:#111}}
  .wrap{{max-width:720px;margin:0 auto;background:#fff;border:1px solid #e5e7eb;border-radius:8px;padding:24px}}
  h1{{font-size:20px;margin:0 0 16px}}
  table{{width:100%;border-collapse:collapse}}
  tr{{border-bottom:1px solid #e5e7eb}}
  td{{padding:12px 8px;vertical-align:top}}
  td.idx{{width:36px;text-align:right;font-weight:600;color:#374151}}
  .title a{{font-weight:600;color:#111;text-decoration:none}}
  .title a:hover{{text-decoration:underline}}
  .prices{{margin-top:6px}}
  .old{{text-decoration:line-through;opacity:.7;margin-right:6px}}
  .new{{font-weight:700}}
  .link{{font-size:12px;color:#6b7280;margin-top:6px;word-break:break-all}}
  .footer{{margin-top:24px;font-size:12px;color:#6b7280}}
</style>
</head>
<body>
  <div class="wrap">
    <h1>Zmiany cen ({len(changes)})</h1>
    <table>{rows}</table>
    <div class="footer">Automat PSStorePrice</div>
  </div>
</body>
</html>"""


def send_email(
    smtp_server: str,
    sender_mail: str,
    sender_pass: str,
    recipient: str,
    changes: list[dict],
) -> None:
    """Wysyla e-mail z lista wykrytych obnizek."""
    message = MIMEMultipart("alternative")
    message["From"] = sender_mail
    message["To"] = recipient
    message["Subject"] = "Promocje w PS Store!"
    message.attach(MIMEText(build_plain_text_body(changes), "plain", "utf-8"))
    message.attach(MIMEText(build_email_html(changes), "html", "utf-8"))

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, 587) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender_mail, sender_pass)
        server.sendmail(sender_mail, [recipient], message.as_string())
