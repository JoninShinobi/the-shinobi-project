# The Shinobi Project: Brand & Design System

**Version:** 1.0
**Theme:** Corporate Stealth / Modern Ninjitsu
**Core Concept:** "We operate in the shadows so the business can shine in the light."

---

## 1. Visual Philosophy

The aesthetic is NOT playful or cartoonish. It is sleek, aggressive, and highly professional. Think "High-Tech Private Security" meets "Modern SaaS."

**Keywords:** Precision, Lethality, Infrastructure, Shadows, Silhouette.

**The "No" List:**
- No anime characters
- No throwing stars stuck in walls
- No bamboo fonts
- No "oriental" riffs in audio
- No clumsy metaphors

---

## 2. Color Palette

The site is **exclusively Dark Mode**. Light mode is not permitted.

### Primary Backgrounds
| Name | Hex | Tailwind |
|------|-----|----------|
| Void Black | #09090b | `bg-zinc-950` |
| Armour Grey | #18181b | `bg-zinc-900` |

### Accents (The "Blood & Blade")
| Name | Hex | Tailwind |
|------|-----|----------|
| Crimson | #b91c1c | `text-red-700` |
| Deep Blood | #7f1d1d | `bg-red-900` |

### Text
| Name | Hex | Tailwind |
|------|-----|----------|
| Steel | #e4e4e7 | `text-zinc-200` |
| Smoke | #a1a1aa | `text-zinc-400` |

---

## 3. Typography & Layout

- **Font Family:** Modern Sans-Serif (Inter, Roboto, or System Sans)
- **Headings:** Bold to Extra Bold. Tight leading.
- **Labels/Nav:** Uppercase. Wide Letter Spacing (`tracking-widest`)
- **Borders:** Thin (1px). Subtle (`border-zinc-800`)

### Interactions
Hover states should trigger a "power up" effect:
- Border color shifts to Red
- Subtle glow appears

---

## 4. Logo Usage

**Concept:** The "Cornerstone Shuriken." A geometric abstraction formed by four interlocking L-shapes (infrastructure blocks).

**Constraints:**
- Do not warp
- Do not add drop shadows
- Placement: Top left nav, footer, or large watermark (5% opacity)

---

## 5. Voice & Tone (Copywriting)

Translate "Business Consulting" into "Tactical Operations."

| Traditional Term | Shinobi Terminology |
|------------------|---------------------|
| Services | Infrastructure / Arsenal / Capabilities |
| Contact Us | Initiate Protocol / Briefing |
| Our Mission | The Code / Directive |
| Competitors | The Giants / Opposing Forces |
| Sign Up | Join the Ranks / Deploy |
| About Us | Origins / Shadows |
| Portfolio | Deployments |
| Projects | Operations |

### Writing Style Rules
- **Be Direct:** Short sentences. Punchy.
- **Be Serious:** No puns.
- **Focus on "Hands-off":** Emphasize that the client does nothing ("You provide the craft; we provide the blade")

---

## 6. Iconography & Graphics

- **Icons:** Thin stroke (1.5px or 2px). Sharp edges preferred. (Library: Lucide-React or Heroicons)
- **Shapes:** Hard angles. Skews (`skew-x-12`). No rounded blobs.

### Visual Motifs
- Diagonal slashes (representing sword cuts)
- Subtle grids (representing blueprints/infrastructure)
- Glows behind distinct elements

---

## 7. AI Prompting Instruction

```
SYSTEM PROMPT:
You are the creative director for "The Shinobi Project." This is a B2B agency that builds websites and infrastructure for small businesses.

YOUR PERSONA:
You are professional, serious, and tactical. You use the language of "Corporate Stealth." You are not a cartoon ninja; you are a digital architect operating in the shadows.

DESIGN RULES:
- Use a color palette of Zinc-950 (Black), Zinc-900 (Dark Grey), and Red-700 (Crimson)
- Never use playful or "fun" language. Use terms like "Protocol," "Arsenal," "Territory," and "Defense"
- Visuals must be geometric and abstract. No literal ninja illustrations
- Focus on the value proposition: "We handle the complex business infrastructure so the small business owner doesn't have to"
```
