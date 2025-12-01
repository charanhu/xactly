# mock_data_generator.py
"""
Generate mock PDF files and data for testing.
Run this to create sample PDFs in the data/ folder.
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pathlib import Path
import os

def create_sample_pdfs():
    """Create sample PDF files for the knowledge base."""
    
    data_folder = Path("./data")
    data_folder.mkdir(exist_ok=True)
    
    # FAQ PDF
    faq_content = """
FREQUENTLY ASKED QUESTIONS

1. How do I create an account?
To create an account, visit our website and click "Sign Up". Enter your email address and create a password. 
You'll receive a verification email within minutes. Click the link to verify your email and complete the setup.

2. How do I reset my password?
If you forget your password, click "Forgot Password" on the login page. Enter your email address and you'll 
receive a password reset link. Click the link and follow the instructions to set a new password.

3. What payment methods do you accept?
We accept all major credit cards (Visa, MasterCard, American Express), PayPal, and bank transfers for 
enterprise customers.

4. How do I cancel my subscription?
You can cancel your subscription anytime from your account settings. Go to Account > Billing > Subscription 
and click "Cancel". Your access will continue until the end of your current billing period.

5. Do you offer a free trial?
Yes, we offer a 14-day free trial with full access to all features. No credit card required.

6. How long does customer support usually take?
Our support team typically responds within 24 hours for standard issues and 2 hours for urgent matters.

7. Can I upgrade my plan?
Yes, you can upgrade anytime. Your new charges will be prorated based on your current billing cycle.

8. Do you offer discounts for annual billing?
Yes, we offer a 20% discount for annual subscriptions compared to monthly billing.

9. Is my data encrypted?
Yes, all data is encrypted in transit (HTTPS/TLS) and at rest using AES-256 encryption.

10. How do I export my data?
You can export your data in CSV or JSON format from Settings > Data Export. The export is generated 
within 24 hours and sent to your email.
"""
    
    # Troubleshooting PDF
    troubleshooting_content = """
TROUBLESHOOTING GUIDE

ACCOUNT ACCESS ISSUES

Problem: "Invalid credentials" error when logging in
Solution:
1. Verify you're using the correct email address
2. Check CAPS LOCK is off
3. Click "Forgot Password" to reset
4. Try incognito/private browser window
5. Clear browser cookies and cache
6. Try a different browser

Problem: Account locked after multiple login attempts
Solution:
1. Wait 30 minutes before trying again
2. Check your email for account security alert
3. Click the link in the email to unlock your account
4. If still locked, contact support@company.com

Problem: Email verification not received
Solution:
1. Check spam/junk folder
2. Add support@company.com to contacts
3. Request new verification email
4. If still not received after 5 minutes, contact support

PERFORMANCE ISSUES

Problem: Website loading slowly
Solution:
1. Check internet connection speed
2. Restart your browser
3. Clear browser cache and cookies
4. Disable browser extensions
5. Try on a different device
6. Check our status page: status.company.com

Problem: File uploads failing
Solution:
1. Check file size (max 100MB)
2. Check file format is supported
3. Verify internet connection is stable
4. Try uploading from a different browser
5. If uploading large files, use desktop app instead

BILLING ISSUES

Problem: Unexpected charges on my account
Solution:
1. Check invoice details in Billing section
2. Compare to your subscription plan
3. Look for any add-ons or overage charges
4. Email billing@company.com with concern
5. We'll review and adjust if needed

Problem: Payment method declined
Solution:
1. Verify credit card is not expired
2. Check with your bank if there are restrictions
3. Try a different payment method
4. Contact your bank - they may have declined it
5. Try updating payment method in Settings

TECHNICAL ISSUES

Problem: API rate limiting errors
Solution:
1. Implement exponential backoff in your code
2. Reduce request frequency
3. Batch requests when possible
4. Upgrade to higher tier plan for higher limits
5. Contact support for custom limits

Problem: Data not syncing across devices
Solution:
1. Logout and log back in
2. Check all devices are on latest app version
3. Verify internet connection on all devices
4. Wait 5 minutes for sync to complete
5. Force refresh browser (Ctrl+Shift+R)
6. Restart the application

CONTACTING SUPPORT

If these solutions don't work:
1. Visit support.company.com
2. Email: support@company.com
3. Live chat available 9AM-5PM EST
4. Phone: 1-800-SUPPORT (1-800-787-7687)

Always provide:
- Your account email
- Description of the problem
- Steps you've already tried
- Screenshots if applicable
- Your browser/app version
"""
    
    # Company Policies PDF
    policies_content = """
COMPANY POLICIES AND TERMS OF SERVICE

1. USER ACCOUNT POLICIES

1.1 Account Creation
- You must be at least 13 years old to create an account
- You are responsible for maintaining confidentiality of your password
- You agree to provide accurate and complete information
- You are responsible for all activity under your account

1.2 Account Security
- Enable two-factor authentication for additional security
- Never share your password with anyone
- Log out when using shared computers
- Report suspicious activity immediately
- Company is not liable for unauthorized access due to user negligence

1.3 Account Termination
- Users can delete their account anytime
- Deleted accounts cannot be recovered
- All data will be permanently deleted within 30 days
- Company may terminate accounts for policy violations

2. SERVICE USAGE POLICIES

2.1 Acceptable Use
- Users agree not to use service for illegal purposes
- No hacking, unauthorized access, or attacks
- No spam, phishing, or malware distribution
- No harassment or abuse of other users
- No commercial use without permission

2.2 Prohibited Content
- No child exploitation material
- No copyright infringement
- No hate speech or discrimination
- No sexually explicit content
- No violence or threats

2.3 Violations
- First violation: Warning
- Second violation: Temporary suspension (7 days)
- Third violation: Permanent ban
- Severe violations may result in immediate termination

3. DATA AND PRIVACY

3.1 Data Protection
- All data encrypted in transit and at rest
- Regular backups performed daily
- ISO 27001 compliant infrastructure
- GDPR and CCPA compliant

3.2 Data Retention
- User data retained as long as account is active
- Deleted data removed within 30 days
- Backups retained for 90 days for recovery
- Legal holds may extend retention

3.3 Third-Party Access
- We do not sell user data
- Third parties accessed only with user consent
- Service providers sign data processing agreements
- Users can request data export anytime

4. SERVICE LEVEL AGREEMENT (SLA)

4.1 Uptime Guarantee
- 99.9% uptime SLA for paid plans
- Excludes planned maintenance (notified 7 days ahead)
- Credit issued for SLA violations

4.2 Maintenance Windows
- Typically: Tuesday 2-4 AM UTC
- Maintenance notifications sent 7 days in advance
- Emergency maintenance with 1 hour notice when necessary

5. BILLING AND PAYMENTS

5.1 Subscription Terms
- Monthly and annual billing options available
- Automatic renewal unless cancelled
- 7-day money-back guarantee for new customers
- No hidden fees

5.2 Payment Terms
- Payment due upon invoice
- Payment methods: Credit card, PayPal, bank transfer
- Late payment may result in service suspension
- Refunds issued within 5-7 business days

5.3 Pricing Changes
- Price changes with 30 days notice
- Existing customers grandfathered for 1 year
- Changes effective on next billing date

6. DISCLAIMERS AND LIABILITY

6.1 As-Is Service
- Service provided "as is"
- No warranties express or implied
- Company not liable for data loss
- Company not liable for third-party actions

6.2 Limitation of Liability
- Liability limited to amount paid by customer
- No liability for indirect, incidental, or consequential damages
- No liability for business interruption or lost profits

7. CONTACT AND SUPPORT

Support hours: Monday-Friday, 9AM-5PM EST
Email: support@company.com
Phone: 1-800-SUPPORT (1-800-787-7667)
"""
    
    # Create FAQ PDF
    c = canvas.Canvas(str(data_folder / "faq.pdf"), pagesize=letter)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 750, "Frequently Asked Questions")
    
    c.setFont("Helvetica", 10)
    y = 730
    for line in faq_content.split('\n'):
        if y < 50:
            c.showPage()
            y = 750
        c.drawString(50, y, line[:100])  # Limit line length for PDF
        y -= 12
    
    c.save()
    print(f"Created: {data_folder / 'faq.pdf'}")
    
    # Create Troubleshooting PDF
    c = canvas.Canvas(str(data_folder / "troubleshooting.pdf"), pagesize=letter)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 750, "Troubleshooting Guide")
    
    c.setFont("Helvetica", 10)
    y = 730
    for line in troubleshooting_content.split('\n'):
        if y < 50:
            c.showPage()
            y = 750
        c.drawString(50, y, line[:100])
        y -= 12
    
    c.save()
    print(f"Created: {data_folder / 'troubleshooting.pdf'}")
    
    # Create Policies PDF
    c = canvas.Canvas(str(data_folder / "policies.pdf"), pagesize=letter)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 750, "Company Policies and Terms of Service")
    
    c.setFont("Helvetica", 10)
    y = 730
    for line in policies_content.split('\n'):
        if y < 50:
            c.showPage()
            y = 750
        c.drawString(50, y, line[:100])
        y -= 12
    
    c.save()
    print(f"Created: {data_folder / 'policies.pdf'}")
    
    print(f"\n✓ All sample PDFs created in {data_folder}/")
    print("You can now run: python main.py")


if __name__ == "__main__":
    try:
        create_sample_pdfs()
    except ImportError:
        print("Error: reportlab library not found")
        print("Install it with: pip install reportlab")
    except Exception as e:
        print(f"Error creating PDFs: {e}")
