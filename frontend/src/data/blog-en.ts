export interface Article {
  slug: string;
  title: string;
  publishedAt: Date;
  tags: string[];
  excerpt: string;
  content: string | null;
}

export const articles: Article[] = [
  {
    slug: 'latenz-falle-asyncio',
    title: 'The Latency Trap: Why Sequential Code Fails in AI Integration',
    publishedAt: new Date('2026-03-19'),
    tags: ['AI Engineering', 'Python', 'AsyncIO', 'Performance'],
    excerpt:
      'When connecting core systems to LLMs today, my CPU barely computes – it just waits. Sequential code becomes a fatal bottleneck. The solution: AsyncIO and the principle of concurrency on a single thread.',
    content: `As a computer science graduate, I learned to think in clear sequences: code is executed line by line. This is safe and deterministic, but in AI Engineering it quickly becomes a fatal bottleneck.

The problem: when connecting core systems to Large Language Models (LLMs) today, my CPU barely computes. It sends HTTP requests and waits for external servers. This is called **I/O-Bound**. If I send 100 documents to an AI one after another and each response takes two seconds, my system freezes completely for over three minutes. Classic multithreading is often too expensive and inefficient for this.

The architectural solution in Python is called **AsyncIO**. Instead of blindly blocking, I use the principle of concurrency on a single thread. Like a good waiter who takes 100 orders and lets the kitchen work instead of standing at the oven waiting for the first pizza, the *Event Loop* delegates the waiting. With \`asyncio.gather()\` I fire hundreds of API calls in quasi-parallel. The wait times overlap, the system never blocks, and minutes turn into seconds.

**Conclusion:** Anyone connecting external AI models or vector databases today can no longer afford sequential waiting. Asynchronous programming is the essential foundation for scalable AI systems.`
  },
  {
    slug: 'determinismus-zu-wahrscheinlichkeit',
    title: 'From Determinism to Probability: Why I\'m Learning to Let Go of Control',
    publishedAt: new Date('2026-03-19'),
    tags: ['AI Engineering', 'LLM', 'Paradigm Shift', 'Software Development'],
    excerpt:
      'When I got my computer science degree, the world was binary: if (x) then y. Today, the shift from absolute logic to probabilities fascinates me – and what that means for an engineer coming from the world of strict typing.',
    content: `When I got my computer science degree over 15 years ago, the world was binary: \`if (x) then y\`. A bug was a logical error in a chain of absolute certainty. We built cathedrals from deterministic code – rigid and safe. The challenge today: designing a system that "understands" what a user means without writing millions of rule sets.

In my current engagement with LLMs, I'm fascinated by the shift from absolute logic to probabilities. It's a **radical paradigm shift**: we no longer program every branch, we define the target corridor. For an engineer coming from the world of strict typing, this is counterintuitive at first – but this is exactly where the new leverage lies.

**The technical bridge:** My approach is to use Pydantic to channel this "probabilistic chaos" into deterministic paths. The AI provides the creative flexibility, but my validation filter ensures the necessary structure of software engineering.

**The feeling:** It's like moving from solo pianist to conductor. You no longer play every note yourself – you orchestrate the intelligence.`
  },
  {
    slug: 'tod-des-boilerplate-burnouts',
    title: 'The Death of Boilerplate Burnout: How AI Gives Us Time Back for Architecture',
    publishedAt: new Date('2026-03-19'),
    tags: ['AI Engineering', 'Productivity', 'Software Development', 'Architecture'],
    excerpt:
      'How many weeks of our professional lives have we spent writing CRUD interfaces or database migrations? AI is massively shifting the focus – away from code-shoveling, toward system design.',
    content: `How many weeks of our professional lives have we spent writing CRUD interfaces or database migrations? Yesterday it was unthinkable to spin up a stable scaffolding in no time.

Through the targeted use of AI assistance in the development process, the focus shifts massively. While AI handles repetitive tasks and standard boilerplate, I can focus on what truly matters: **System design**. How do vector embeddings scale? What does a robust RAG strategy look like?

**The technical bridge:** In my portfolio project, I use Astro Islands and asynchronous Python to keep overhead minimal. AI serves here as a highly efficient assistant for standard tasks, leaving room for real architectural decisions.

**The feeling:** It's liberating. We no longer need to be "code shovelers." After 15 years of experience, I feel how AI gives me back the time to think about the big problems.`
  },
  {
    slug: 'wenn-code-mitdenkt',
    title: 'When Code Suddenly "Thinks Along": The New Era of Contextual Understanding',
    publishedAt: new Date('2026-03-19'),
    tags: ['AI Engineering', 'LLM', 'Vision API', 'Contextual Understanding'],
    excerpt:
      'In classical software development, there were no nuances. Today, I\'m exploring in my AI showcase experiments how an agent recognizes the urgency of a request and adjusts workflow priority accordingly.',
    content: `In classical software development, there were no nuances. An input was either valid or invalid. The idea that a system could grasp the context of a situation – for example, recognizing the urgency of a request and adjusting a workflow's priority accordingly – was long considered pure theory.

In my current AI Showcase experiments, I'm probing exactly these boundaries. When an agent uses tools to translate a vague user request into a precise action, we leave the world of simple logic. It's about **simulated understanding** and situational adaptation.

**The technical bridge:** I'm experimenting here with the combination of Vision APIs and sentiment analysis. A screenshot or message is analyzed not just to extract data, but to grasp the user's intention.

**The feeling:** There's this moment when the AI recognizes a nuance that wasn't explicitly coded. Software transforms from a rigid tool into a thinking partner.`
  },
  {
    slug: 'typescript-zu-pydantic',
    title: 'From TypeScript to Pydantic: My Journey from Deterministic Software to Probabilistic AI',
    publishedAt: new Date('2026-03-18'),
    tags: ['AI Engineering', 'Python', 'Pydantic', 'TypeScript'],
    excerpt:
      'As a computer science graduate, my journey started deterministically: object-oriented design, fixed contracts, predictable systems. On my current path into AI Engineering, I face a new architectural break – and Pydantic is the bridge.',
    content: `As a computer science graduate, my journey started deterministically: object-oriented design, fixed contracts, predictable systems. With JavaScript and the principle of "Duck Typing", the dynamic freedom of web development arrived – along with cascading runtime errors from missing type safety. The industry responded with **TypeScript**: Compile-time safety brought back control. Contracts in code became reliable again.

On my current path into AI Engineering with Python, I now face a new architectural break: deterministic core systems (databases, APIs) collide with **probabilistic** Large Language Models (LLMs).

An LLM has no fixed data types; it generates free text based on probabilities. Static compiler checks like those in TypeScript miss the mark here, since the data is only generated at runtime by the AI (and potentially hallucinated). Anyone who blindly routes unvalidated LLM output into their systems risks fatal data corruption.

The architectural bridge for this problem is called **Pydantic**. It translates Python's static type hints into relentless runtime validation. If the LLM fails to meet the defined data schema, the system does not crash. Instead, Pydantic throws a structured \`ValidationError\`. I use this architecturally to send it back to the model as an automated correction prompt (*Self-Correction Loop*).

**Conclusion:** The most important lesson from the evolution of JavaScript to TypeScript remains: robust systems need strict contracts. Pydantic is that contract for the AI era – it makes the unpredictable predictable.`
  },

].sort((a, b) => b.publishedAt.getTime() - a.publishedAt.getTime());
