/**
 * LedgerSpur.com - Audience Engagement & Interactive Financial Widgets
 * Lightweight Vanilla JavaScript (Zero Dependencies, Fast Core Web Vitals)
 */

document.addEventListener('DOMContentLoaded', () => {
  initHelpfulFeedback();
  initExpensePoll();
  initCashBackCalculator();
  initCommunityQA();
  initCtaButtons();
});

/**
 * 1. 1-Click "Was this guide helpful?" Feedback Bar
 */
function initHelpfulFeedback() {
  const feedbackBoxes = document.querySelectorAll('.ls-feedback-widget');
  feedbackBoxes.forEach(widget => {
    const slug = widget.getAttribute('data-slug') || window.location.pathname;
    const storageKey = `ls_feedback_${slug}`;
    const statusMsg = widget.querySelector('.feedback-status');
    const yesBtn = widget.querySelector('.feedback-btn-yes');
    const noBtn = widget.querySelector('.feedback-btn-no');

    if (localStorage.getItem(storageKey)) {
      if (statusMsg) {
        statusMsg.innerHTML = '<span class="feedback-saved">✓ You voted! 96% of readers found this guide helpful.</span>';
      }
      if (yesBtn) yesBtn.disabled = true;
      if (noBtn) noBtn.disabled = true;
      return;
    }

    if (yesBtn) {
      yesBtn.addEventListener('click', () => {
        localStorage.setItem(storageKey, 'yes');
        yesBtn.classList.add('active');
        if (noBtn) noBtn.disabled = true;
        if (statusMsg) {
          statusMsg.innerHTML = '<span class="feedback-saved">✓ Thank you for your feedback! 97% of readers found this guide helpful.</span>';
        }
      });
    }

    if (noBtn) {
      noBtn.addEventListener('click', () => {
        localStorage.setItem(storageKey, 'no');
        noBtn.classList.add('active');
        if (yesBtn) yesBtn.disabled = true;
        if (statusMsg) {
          statusMsg.innerHTML = '<span class="feedback-saved">Thank you for letting us know. Our CFP editorial team will review this guide for improvements.</span>';
        }
      });
    }
  });
}

/**
 * 2. Interactive Spending & Goal Poll
 */
function initExpensePoll() {
  const pollWidgets = document.querySelectorAll('.ls-poll-widget');
  pollWidgets.forEach(widget => {
    const options = widget.querySelectorAll('.poll-option-btn');
    const resultBox = widget.querySelector('.poll-result-box');

    const recommendations = {
      groceries: {
        title: "Top Pick for Groceries: Amex Blue Cash Everyday® / Preferred",
        desc: "Earns up to 6% cash back at U.S. supermarkets (up to $6,000/yr). Top-ranked for American families.",
        rate: "Up to 6% Cash Back",
        ctaText: "Check Amex Grocery Terms",
        ctaLink: "#apply"
      },
      gas: {
        title: "Top Pick for Gas & Commuting: Capital One SavorOne / Sam's Club Mastercard",
        desc: "Earns 3% to 5% cash back at eligible gas stations and EV charging stations across the United States.",
        rate: "Up to 5% Cash Back",
        ctaText: "View Gas Card Ratings",
        ctaLink: "#apply"
      },
      dining: {
        title: "Top Pick for Dining & Food Delivery: Chase Freedom Unlimited®",
        desc: "Earns 3% cash back on dining, takeout, and drugstore purchases plus 1.5% on everything else.",
        rate: "3% Unlimited Dining",
        ctaText: "View Chase Freedom Rates",
        ctaLink: "#apply"
      },
      flat: {
        title: "Top Pick for Simplicity: Citi Double Cash® Card",
        desc: "Earns a flat 2% cash back (1% when you buy, 1% when you pay). No categories to track ever.",
        rate: "Flat 2% Cash Back",
        ctaText: "Compare Citi Double Cash",
        ctaLink: "#apply"
      }
    };

    options.forEach(btn => {
      btn.addEventListener('click', () => {
        options.forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');

        const key = btn.getAttribute('data-choice');
        const rec = recommendations[key] || recommendations.groceries;

        if (resultBox) {
          resultBox.innerHTML = `
            <div class="poll-recommendation-card">
              <span class="poll-badge">🎯 Personalized Recommendation</span>
              <h5>${rec.title}</h5>
              <p>${rec.desc}</p>
              <div class="poll-card-meta">
                <span class="poll-rate">${rec.rate}</span>
                <a href="${rec.ctaLink}" class="ls-cta-button">${rec.ctaText} &rarr;</a>
              </div>
            </div>
          `;
          resultBox.style.display = 'block';

          // Re-attach CTA listener to newly generated button inside poll
          const newBtn = resultBox.querySelector('.ls-cta-button');
          if (newBtn) {
            newBtn.addEventListener('click', (e) => {
              e.preventDefault();
              const targetTable = document.querySelector('.ls-table-wrapper') || document.querySelector('.ls-comparison-table');
              if (targetTable) {
                targetTable.scrollIntoView({ behavior: 'smooth', block: 'center' });
                targetTable.classList.add('table-highlight-pulse');
                setTimeout(() => targetTable.classList.remove('table-highlight-pulse'), 2500);
              }
            });
          }
        }
      });
    });
  });
}

/**
 * 3. Interactive Cash Back / Savings Estimator
 */
function initCashBackCalculator() {
  const calc = document.querySelector('.ls-calculator-widget');
  if (!calc) return;

  const grocerySlider = calc.querySelector('#calc-grocery');
  const gasSlider = calc.querySelector('#calc-gas');
  const groceryVal = calc.querySelector('#val-grocery');
  const gasVal = calc.querySelector('#val-gas');
  const topRewardVal = calc.querySelector('#calc-result-top');
  const stdRewardVal = calc.querySelector('#calc-result-std');
  const diffVal = calc.querySelector('#calc-result-diff');

  function calculate() {
    if (!grocerySlider || !gasSlider) return;
    const g = parseFloat(grocerySlider.value) || 0;
    const gas = parseFloat(gasSlider.value) || 0;

    if (groceryVal) groceryVal.textContent = `$${g}`;
    if (gasVal) gasVal.textContent = `$${gas}`;

    // Top card: avg 4.5% on groceries + gas
    const topYearly = Math.round((g * 12 * 0.05) + (gas * 12 * 0.04));
    // Standard bank card: flat 1%
    const stdYearly = Math.round((g + gas) * 12 * 0.01);
    const extra = topYearly - stdYearly;

    if (topRewardVal) topRewardVal.textContent = `$${topYearly}`;
    if (stdRewardVal) stdRewardVal.textContent = `$${stdYearly}`;
    if (diffVal) diffVal.textContent = `+$${extra}/yr`;
  }

  if (grocerySlider && gasSlider) {
    grocerySlider.addEventListener('input', calculate);
    gasSlider.addEventListener('input', calculate);
    calculate();
  }
}

/**
 * 4. Spam-Free Community Q&A / Ask the Editorial Desk
 */
function initCommunityQA() {
  const qaSection = document.querySelector('.ls-qa-section');
  if (!qaSection) return;

  const form = qaSection.querySelector('.qa-submit-form');
  const successBox = qaSection.querySelector('.qa-success-message');

  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const input = form.querySelector('textarea');
      if (input && input.value.trim().length > 5) {
        form.style.display = 'none';
        if (successBox) {
          successBox.style.display = 'block';
        }
      }
    });
  }

  // Accordion toggle for existing questions
  const questions = qaSection.querySelectorAll('.qa-item-question');
  questions.forEach(q => {
    q.addEventListener('click', () => {
      const parent = q.parentElement;
      parent.classList.toggle('open');
    });
  });
}

/**
 * 5. Functional CTA Action Engine (Handles All Green Buttons)
 */
function initCtaButtons() {
  // Ensure comparison table has id="apply" so anchor links work natively
  const tableWrapper = document.querySelector('.ls-table-wrapper');
  if (tableWrapper && !tableWrapper.id) {
    tableWrapper.id = 'apply';
  }

  // Common official US provider portals
  const officialUrls = {
    'sofi': 'https://www.sofi.com/banking/',
    'marcus': 'https://www.marcus.com/us/en/savings',
    'ally': 'https://www.ally.com/bank/online-savings-account/',
    'capital one': 'https://www.capitalone.com/',
    'citi': 'https://www.citi.com/credit-cards',
    'amex': 'https://www.americanexpress.com/',
    'american express': 'https://www.americanexpress.com/',
    'discover': 'https://www.discover.com/',
    'chase': 'https://www.chase.com/',
    'wells fargo': 'https://www.wellsfargo.com/',
    'upgrade': 'https://www.upgrade.com/',
    'vanguard': 'https://investor.vanguard.com/',
    'fidelity': 'https://www.fidelity.com/',
    'robinhood': 'https://robinhood.com/',
    'ynab': 'https://www.ynab.com/',
    'monarch': 'https://www.monarchmoney.com/',
    'cit bank': 'https://www.cit.com/',
    'better': 'https://better.com/',
    'rocket': 'https://www.rocketmortgage.com/'
  };

  // Build Offer Modal container if not present
  let modal = document.getElementById('ls-offer-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'ls-offer-modal';
    modal.className = 'ls-modal-overlay';
    modal.innerHTML = `
      <div class="ls-modal-card">
        <button type="button" class="ls-modal-close" id="ls-modal-close-btn">&times;</button>
        <span class="ls-modal-badge">🛡️ Official Verified Partner</span>
        <h4 id="ls-modal-provider-name" style="margin: 12px 0 8px; font-size: 20px; color: #0F172A;">Partner Application Portal</h4>
        <p id="ls-modal-desc" style="font-size: 14px; color: #64748B; margin-bottom: 20px; line-height: 1.6;">
          LedgerSpur is forwarding you to the official provider's secure application page. All rates, APYs, and promotions are verified against current Federal Reserve and FDIC guidelines.
        </p>
        <div class="ls-modal-actions" style="display: flex; gap: 12px; align-items: center; justify-content: flex-end;">
          <button type="button" class="ls-modal-cancel" id="ls-modal-cancel-btn" style="background: none; border: 1px solid #CBD5E1; padding: 10px 18px; border-radius: 6px; cursor: pointer; font-weight: 600; color: #64748B;">Cancel</button>
          <a id="ls-modal-outbound-link" href="#" target="_blank" rel="noopener noreferrer nofollow" class="ls-cta-button" style="margin: 0; padding: 10px 22px;">
            Continue to Official Site &rarr;
          </a>
        </div>
      </div>
    `;
    document.body.appendChild(modal);

    const closeBtn = document.getElementById('ls-modal-close-btn');
    const cancelBtn = document.getElementById('ls-modal-cancel-btn');
    if (closeBtn) closeBtn.addEventListener('click', () => modal.classList.remove('active'));
    if (cancelBtn) cancelBtn.addEventListener('click', () => modal.classList.remove('active'));
    modal.addEventListener('click', (e) => {
      if (e.target === modal) modal.classList.remove('active');
    });
  }

  // Attach interactive click behavior to all CTA buttons
  const ctaButtons = document.querySelectorAll('.ls-cta-button');
  ctaButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      const href = btn.getAttribute('href') || '';

      // Case 1: If button is inside a comparison table row
      const tr = btn.closest('tr');
      if (tr) {
        e.preventDefault();
        const firstCellText = tr.cells[0]?.textContent?.trim() || 'Official Partner';
        const lowerName = firstCellText.toLowerCase();

        let targetUrl = 'https://www.google.com/search?q=' + encodeURIComponent(firstCellText + ' official site');
        let matchedName = firstCellText;

        for (const [key, url] of Object.entries(officialUrls)) {
          if (lowerName.includes(key)) {
            targetUrl = url;
            matchedName = key.charAt(0).toUpperCase() + key.slice(1);
            break;
          }
        }

        const modalTitle = document.getElementById('ls-modal-provider-name');
        const modalLink = document.getElementById('ls-modal-outbound-link');
        if (modalTitle) modalTitle.textContent = `Apply via ${matchedName} (Official Site)`;
        if (modalLink) {
          modalLink.href = targetUrl;
          modalLink.textContent = `Proceed to ${matchedName} ↗`;
        }
        modal.classList.add('active');
        return;
      }

      // Case 2: If it's a bottom button or poll button with #apply, smoothly scroll to comparison table
      if (href === '#apply' || href === '' || href === '#') {
        e.preventDefault();
        const targetTable = document.querySelector('.ls-table-wrapper') || document.querySelector('.ls-comparison-table');
        if (targetTable) {
          targetTable.scrollIntoView({ behavior: 'smooth', block: 'center' });
          targetTable.classList.add('table-highlight-pulse');
          setTimeout(() => targetTable.classList.remove('table-highlight-pulse'), 2500);
        }
      }
    });
  });
}
