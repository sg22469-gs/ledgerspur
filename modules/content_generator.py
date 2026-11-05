import os
import re
import time
from google import genai
from config import Config

class ContentGenerator:
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        self.model_name = Config.GEMINI_MODEL or "gemini-3.8-flash"
        self.client = genai.Client(api_key=self.api_key)

    def generate_article(self, topic_data: dict) -> dict:
        """
        Generates a 1,500+ word, SEO-optimized, E-E-A-T compliant US finance article.
        """
        topic = topic_data.get("topic")
        category = topic_data.get("category", "Banking")
        keyword = topic_data.get("target_keyword", topic)
        affiliate_focus = topic_data.get("affiliate_focus", "Top US Providers")

        system_instruction = (
            "You are a Senior Financial Analyst and Certified Financial Planner (CFP) writing exclusively "
            "for LedgerSpur.com (Smart Money. Sharper Moves.), a premier US financial publication. "
            "Your audience consists of American consumers, young professionals, and savers seeking unbiased, "
            "data-driven financial guidance. "
            "You write in clear, engaging, conversational American English (en-US). "
            "Never use generic fluff like 'In today's fast-paced world' or repetitive introductions. "
            "Always maintain rigorous E-E-A-T standards (Experience, Expertise, Authoritativeness, Trustworthiness)."
        )

        prompt = f"""
Write an in-depth, high-converting, authoritative guide on the topic:
"{topic}"

Target Primary Keyword: "{keyword}"
Category: "{category}"
Key Products/Entities to evaluate: "{affiliate_focus}"

STRUCTURE REQUIREMENTS (Strictly output clean, valid semantic HTML):

1. Dynamic FTC Affiliate Disclosure:
<div class="ls-disclosure">
  <strong>Advertiser Disclosure:</strong> LedgerSpur is an independent, advertising-supported publisher. We may receive compensation from partners when you click links or open accounts reviewed below. This does not impact our editorial ratings or interest rate calculations.
</div>

2. Key Takeaways Box (Immediately in the first 100 words):
<div class="ls-takeaways-box">
  <h4>💡 Key Takeaways</h4>
  <ul>
    <li>Bullet point with top pick or quick answer</li>
    <li>Bullet point with key metric (e.g. APY, APR, or minimum deposit)</li>
    <li>Bullet point with our bottom-line verdict</li>
  </ul>
</div>

3. Comprehensive Introduction:
Provide a clear, authoritative hook explaining why this matters for the reader's wallet right now.

4. Side-by-Side Comparison Table:
<div class="ls-table-wrapper">
  <table class="ls-comparison-table">
    <thead>
      <tr>
        <th>Provider / Card</th>
        <th>Key Feature (APY / Reward)</th>
        <th>Fees / Min Deposit</th>
        <th>Best For</th>
        <th>Action</th>
      </tr>
    </thead>
    <tbody>
      <!-- At least 3-4 realistic US financial institutions (e.g. SoFi, Marcus, Ally, Capital One) -->
      <!-- Include a link styled with class="ls-cta-button" -->
    </tbody>
  </table>
</div>

5. Detailed In-Depth Breakdown (H2 and H3 tags):
Analyze each top contender in detail. For each, include:
- Overview and key benefits
- Fee structures and eligibility requirements
- A Pros & Cons Grid:
<div class="ls-pros-cons-grid">
  <div class="ls-pros-card">
    <h5>✓ Pros</h5>
    <ul><li>Benefit 1</li><li>Benefit 2</li></ul>
  </div>
  <div class="ls-cons-card">
    <h5>✗ Cons</h5>
    <ul><li>Drawback 1</li><li>Drawback 2</li></ul>
  </div>
</div>

6. How to Choose & Insider Strategy:
Step-by-step checklist for the consumer to maximize their returns or protect their credit score.

7. Frequently Asked Questions (FAQ Section - At least 3 questions):
Use clear H3 tags for questions and detailed answers matching Google's "People Also Ask".

8. Final Verdict & Contextual Call-to-Action:
Summarize the decision with a closing <a href="#apply" class="ls-cta-button">View Current Rates on LedgerSpur</a>.

9. JSON-LD Schema:
At the very end of the output, include a script tag with valid JSON-LD schema for Article and FAQPage.

IMPORTANT: Output ONLY the HTML content. Do NOT wrap inside markdown backticks (```html). Start directly with the first HTML tag.
"""

        models_to_try = [
            self.model_name,
            "gemini-3.6-flash",
            "gemini-3.5-flash",
            "gemini-3.1-flash-lite",
            "gemini-flash-lite-latest",
            "gemini-3.5-flash-lite",
            "gemini-3.8-flash",
        ]
        # Deduplicate preserving order
        unique_models = []
        for m in models_to_try:
            if m and m not in unique_models:
                unique_models.append(m)

        response = None
        for current_model in unique_models:
            for attempt in range(2):
                try:
                    response = self.client.models.generate_content(
                        model=current_model,
                        contents=prompt,
                        config={
                            "system_instruction": system_instruction,
                            "temperature": 0.7,
                        }
                    )
                    if response and response.text:
                        print(f"[+] Successfully generated article using model: {current_model}")
                        break
                except Exception as e:
                    print(f"[!] Warning: Model {current_model} (attempt {attempt+1}) failed ({e})")
                    if attempt == 0:
                        time.sleep(2)
            if response and response.text:
                break

        if not response or not response.text:
            print("[!] All AI models temporarily unavailable or rate-limited. Activating LedgerSpur E-E-A-T Editorial Engine...")
            content = self._generate_fallback_article(topic_data)
        else:
            content = response.text.strip()
            # Clean any accidental markdown backticks
            if content.startswith("```html"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

        # Generate a clean meta description
        meta_description = f"Complete review and guide on {topic} for US consumers by LedgerSpur Editorial."
        for current_model in unique_models:
            try:
                meta_prompt = f"Write a 150-character SEO meta description for this US finance article: '{topic}'. Do not include quotes."
                meta_resp = self.client.models.generate_content(
                    model=current_model,
                    contents=meta_prompt
                )
                if meta_resp and meta_resp.text:
                    meta_description = meta_resp.text.strip().replace('"', '')
                    break
            except Exception:
                continue

        slug = re.sub(r'[^a-zA-Z0-9]+', '-', topic.lower()).strip('-')

        return {
            "title": topic,
            "category": category,
            "tags": topic_data.get("tags", [category, "Finance"]),
            "slug": slug,
            "meta_description": meta_description,
            "html_content": content,
        }

    def _generate_fallback_article(self, topic_data: dict) -> str:
        """Emergency high-quality fallback guide in case of third-party API outage."""
        topic = topic_data.get("topic", "US Personal Finance Guide")
        category = topic_data.get("category", "Banking")
        keyword = topic_data.get("target_keyword", topic)
        affiliate_focus = topic_data.get("affiliate_focus", "Top US Providers")

        return f"""
<div class="ls-disclosure">
  <strong>Advertiser Disclosure:</strong> LedgerSpur is an independent, advertising-supported publisher. We may receive compensation from partners when you click links or open accounts reviewed below. This does not impact our editorial ratings or interest rate calculations.
</div>

<div class="ls-takeaways-box">
  <h4>💡 Key Takeaways</h4>
  <ul>
    <li><strong>Top Recommendation:</strong> Compare fixed-rate yields against flexible cash instruments to lock in optimal APYs.</li>
    <li><strong>FDIC Security:</strong> Always ensure accounts are insured up to $250,000 per depositor by the US Government.</li>
    <li><strong>Bottom Line:</strong> Align your investment timeline with liquidity requirements before committing capital in 2026.</li>
  </ul>
</div>

<p>When navigating <strong>{topic}</strong>, American consumers and savers face critical decisions regarding interest rates, liquidity, and safety. Understanding how current economic trends and Federal Reserve policies influence products like {affiliate_focus} is vital for optimizing cash reserves.</p>

<h2>Why Understanding {topic} Matters Right Now</h2>
<p>In the current macroeconomic environment, interest rate fluctuations dictate the true purchasing power of your savings. Cash left in a standard checking account earning 0.01% APY actively loses purchasing power to inflation. By strategically evaluating <em>{keyword}</em>, you can guarantee superior returns while maintaining peace of mind.</p>

<div class="ls-table-wrapper">
  <table class="ls-comparison-table">
    <thead>
      <tr>
        <th>Provider / Option</th>
        <th>Expected Yield (APY)</th>
        <th>Minimum Deposit</th>
        <th>Liquidity Profile</th>
        <th>Action</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Tier 1 High-Yield Partner</strong></td>
        <td>4.50% - 5.00% APY</td>
        <td>$0</td>
        <td>Daily Access / Flexible</td>
        <td><a href="#apply" class="ls-cta-button">Check Current Rates</a></td>
      </tr>
      <tr>
        <td><strong>Direct US Treasury / CD</strong></td>
        <td>4.75% - 5.20% Fixed</td>
        <td>$100 - $1,000</td>
        <td>Fixed Term (3 to 12 Mo)</td>
        <td><a href="#apply" class="ls-cta-button">Lock In Yield</a></td>
      </tr>
      <tr>
        <td><strong>Federal Credit Union</strong></td>
        <td>4.40% - 4.85% APY</td>
        <td>$25</td>
        <td>NCUA Insured / Liquid</td>
        <td><a href="#apply" class="ls-cta-button">Explore Options</a></td>
      </tr>
    </tbody>
  </table>
</div>

<h2>Core Criteria for Evaluating Your Choices</h2>
<p>To maximize your return on investment while mitigating risk, prioritize these four pillars:</p>
<ol>
  <li><strong>Federal Insurance:</strong> Always verify FDIC insurance for banking products or NCUA/Treasury backing.</li>
  <li><strong>Penalty Structures:</strong> Examine early withdrawal penalties before locking funds into fixed-term options.</li>
  <li><strong>Compounding Frequency:</strong> Daily compounding delivers significantly higher annual yields than monthly or quarterly calculations.</li>
  <li><strong>State Tax Advantages:</strong> Certain federal instruments (such as Treasury Bills) are 100% exempt from state and local income taxes.</li>
</ol>

<div class="ls-pros-cons-grid">
  <div class="ls-pros-card">
    <h5>✓ Advantages</h5>
    <ul>
      <li>Guaranteed, predictable returns backed by high institutional safety.</li>
      <li>Protection against sudden Federal Reserve rate cuts when locking in terms.</li>
      <li>Zero market volatility compared to equity investments.</li>
    </ul>
  </div>
  <div class="ls-cons-card">
    <h5>✗ Considerations</h5>
    <ul>
      <li>Early withdrawal may forfeit up to 3-6 months of earned interest.</li>
      <li>Fixed rates do not capture subsequent interest rate increases.</li>
    </ul>
  </div>
</div>

<h2>Step-by-Step Action Plan</h2>
<p>Follow this checklist to implement your cash strategy effectively:</p>
<ul>
  <li><strong>Step 1:</strong> Calculate your immediate emergency reserve (3 to 6 months of living expenses) and keep this portion fully liquid.</li>
  <li><strong>Step 2:</strong> Allocate secondary cash surplus into laddered fixed-yield instruments to capture peak rates.</li>
  <li><strong>Step 3:</strong> Review maturity dates every quarter to reinvest at the most competitive available APY.</li>
</ul>

<h2>Frequently Asked Questions (FAQ)</h2>
<h3>Is my money completely safe in these financial instruments?</h3>
<p>Yes. Bank accounts reviewed by LedgerSpur are FDIC-insured up to $250,000 per depositor, per insured bank. Direct Treasury securities are backed by the full faith and credit of the United States Government.</p>

<h3>How do state and local taxes impact my net earnings?</h3>
<p>Interest from standard bank CDs and savings accounts is subject to federal, state, and local taxes. However, US Treasury interest is completely exempt from state and local income taxes, making it especially lucrative for residents in high-tax states like California and New York.</p>

<h3>Can I access my funds before maturity?</h3>
<p>Most fixed instruments allow early withdrawal subject to a penalty (typically 90 to 180 days of simple interest). For unconditional liquidity, consider high-yield savings accounts or money market accounts.</p>

<h2>Final Verdict &amp; Recommendation</h2>
<p>For savers seeking the perfect balance between risk, yield, and liquidity, evaluating <strong>{topic}</strong> is a non-negotiable step toward financial independence. Ensure your accounts are structured to capture current high yields while the market window remains open.</p>
<p style="text-align: center; margin: 30px 0;">
  <a href="#apply" class="ls-cta-button">View Current Rates on LedgerSpur &rarr;</a>
</p>
"""

    def generate_fallback_direct(self, topic_data: dict) -> dict:
        """Returns a complete structured article dict in emergency fallback mode."""
        topic = topic_data.get("topic", "US Personal Finance Guide")
        category = topic_data.get("category", "Banking")
        slug = re.sub(r'[^a-zA-Z0-9]+', '-', topic.lower()).strip('-')
        html = self._generate_fallback_article(topic_data)
        return {
            "title": topic,
            "category": category,
            "tags": topic_data.get("tags", [category, "Finance"]),
            "slug": slug,
            "meta_description": f"Complete guide on {topic} for US consumers by LedgerSpur Editorial Desk.",
            "html_content": html,
        }

