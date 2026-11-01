import os
import re
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

        models_to_try = [self.model_name, "gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-3.8-flash"]
        # Deduplicate preserving order
        unique_models = []
        for m in models_to_try:
            if m and m not in unique_models:
                unique_models.append(m)

        response = None
        for current_model in unique_models:
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
                    break
            except Exception as e:
                print(f"[!] Warning: Model {current_model} failed ({e}), trying fallback...")
                continue

        if not response or not response.text:
            raise RuntimeError("Failed to generate content with all available models.")

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
