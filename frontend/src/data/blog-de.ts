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
    title: 'Die Latenz-Falle: Warum sequenzieller Code in der KI-Integration scheitert',
    publishedAt: new Date('2026-03-19'),
    tags: ['AI Engineering', 'Python', 'AsyncIO', 'Performance'],
    excerpt:
      'Wenn ich heute Kernsysteme mit LLMs verbinde, rechnet meine CPU kaum noch – sie wartet. Sequenzieller Code wird zum fatalen Flaschenhals. Die Lösung: AsyncIO und das Prinzip der Nebenläufigkeit auf einem einzigen Thread.',
    content: `Als Diplom-Informatiker habe ich gelernt, in klaren Sequenzen zu denken: Der Code wird Zeile für Zeile abgearbeitet. Das ist sicher und deterministisch, wird im AI Engineering aber schnell zum fatalen Flaschenhals.

Das Problem: Wenn ich heute Kernsysteme mit Large Language Models (LLMs) verbinde, rechnet meine CPU kaum noch. Sie sendet HTTP-Requests und wartet auf externe Server. Das nennt man **I/O-Bound**. Sende ich 100 Dokumente nacheinander an eine KI und jede Antwort dauert zwei Sekunden, friert mein System für über drei Minuten komplett ein. Klassisches Multithreading ist hierfür oft zu teuer und ineffizient.

Die architektonische Lösung in Python heißt **AsyncIO**. Statt blind zu blockieren, nutze ich das Prinzip der Nebenläufigkeit (Concurrency) auf einem einzigen Thread. Wie ein guter Kellner, der 100 Bestellungen aufnimmt und die Küche arbeiten lässt, anstatt vor dem Ofen auf die erste Pizza zu warten, delegiert die *Event Loop* das Warten. Mit \`asyncio.gather()\` feuere ich hunderte API-Aufrufe quasi-parallel ab. Die Wartezeiten überlappen sich, das System blockiert nie, und aus Minuten werden Sekunden.

**Fazit:** Wer heute externe KI-Modelle oder Vektordatenbanken anbindet, kann sich sequenzielles Warten nicht mehr leisten. Asynchrone Programmierung ist das zwingende Fundament für skalierbare KI-Systeme.`
  },
  {
    slug: 'determinismus-zu-wahrscheinlichkeit',
    title: 'Vom Determinismus zur Wahrscheinlichkeit: Warum ich lerne, die Kontrolle abzugeben',
    publishedAt: new Date('2026-03-19'),
    tags: ['AI Engineering', 'LLM', 'Paradigmenwechsel', 'Softwareentwicklung'],
    excerpt:
      'Als ich mein Diplom in Informatik machte, war die Welt binär: if (x) then y. Heute fasziniert mich der radikale Wechsel von absoluter Logik zu Wahrscheinlichkeiten – und was das für einen Ingenieur aus der Welt der strikten Typisierung bedeutet.',
    content: `Als ich vor über 15 Jahren mein Diplom in Informatik machte, war die Welt binär: \`if (x) then y\`. Ein Bug war ein logischer Fehler in einer Kette von absoluter Gewissheit. Wir bauten Kathedralen aus deterministischem Code – starr und sicher. Die Herausforderung heute: Ein System zu entwerfen, das "versteht", was ein Nutzer meint, ohne dass wir Millionen von Regelsätzen schreiben.

In meiner aktuellen Auseinandersetzung mit LLMs fasziniert mich der Wechsel von absoluter Logik zu Wahrscheinlichkeiten. Es ist ein **radikaler Paradigmenwechsel**: Wir programmieren nicht mehr jede Abzweigung, wir definieren den Zielkorridor. Für einen Ingenieur, der aus der Welt der strikten Typisierung kommt, ist das erst einmal kontraintuitiv – aber genau hier liegt die neue Hebelwirkung.

**Die technische Brücke:** Mein Ansatz ist es, Pydantic zu nutzen, um dieses "probabilistische Chaos" in deterministische Bahnen zu lenken. Die KI liefert die kreative Flexibilität, aber mein Validierungs-Filter sorgt für die notwendige Struktur des Software-Engineerings.

**Das Gefühl:** Es ist, als würde man vom Solo-Pianisten zum Dirigenten. Man spielt nicht mehr jede Note selbst, sondern orchestriert die Intelligenz.`
  },
  {
    slug: 'tod-des-boilerplate-burnouts',
    title: 'Der Tod des Boilerplate-Burnouts: Wie KI uns die Zeit für Architektur zurückgibt',
    publishedAt: new Date('2026-03-19'),
    tags: ['AI Engineering', 'Produktivität', 'Softwareentwicklung', 'Architektur'],
    excerpt:
      'Wie viele Wochen unseres Berufslebens haben wir damit verbracht, CRUD-Schnittstellen oder Datenbank-Migrationen zu schreiben? KI verschiebt den Fokus massiv – weg vom Code-Schaufeln, hin zum Systemdesign.',
    content: `Wie viele Wochen unseres Berufslebens haben wir damit verbracht, CRUD-Schnittstellen oder Datenbank-Migrationen zu schreiben? Gestern war es undenkbar, ein stabiles Grundgerüst in kürzester Zeit hochzuziehen.

Durch den gezielten Einsatz von KI-Unterstützung im Development-Prozess verschiebt sich der Fokus massiv. Während die KI repetitive Aufgaben und Standard-Boilerplate übernimmt, kann ich mich auf das konzentrieren, was wirklich zählt: Das **Systemdesign**. Wie skalieren die Vektor-Embeddings? Wie sieht eine robuste RAG-Strategie aus?

**Die technische Brücke:** In meinem Portfolio-Projekt nutze ich Astro Islands und asynchrones Python, um den Overhead minimal zu halten. Die KI dient hier als hocheffizienter Assistent für Standardaufgaben, damit Raum für echte Architektur-Entscheidungen bleibt.

**Das Gefühl:** Es ist eine Befreiung. Wir müssen keine "Code-Schaufler" mehr sein. Nach 15 Jahren Erfahrung spüre ich, wie die KI mir die Zeit zurückgibt, um über die großen Probleme nachzudenken.`
  },
  {
    slug: 'wenn-code-mitdenkt',
    title: 'Wenn Code plötzlich "mitdenkt": Die neue Ära des Kontextverständnisses',
    publishedAt: new Date('2026-03-19'),
    tags: ['AI Engineering', 'LLM', 'Vision API', 'Kontextverständnis'],
    excerpt:
      'In der klassischen Softwareentwicklung gab es keine Nuancen. Heute lote ich in meinen AI Showcase Experimenten aus, wie ein Agent die Dringlichkeit einer Anfrage erkennt und daraufhin die Priorität eines Workflows anpasst.',
    content: `In der klassischen Softwareentwicklung gab es keine Nuancen. Ein Input war valide oder invalid. Dass ein System den Kontext einer Situation erfasst – zum Beispiel die Dringlichkeit in einer Anfrage erkennt und daraufhin die Priorität eines Workflows anpasst – war lange Zeit reine Theorie.

In meinen aktuellen AI Showcase Experimenten lote ich genau diese Grenzen aus. Wenn ein Agent Tools nutzt, um eine vage Nutzeranfrage in eine präzise Aktion zu übersetzen, verlassen wir die Welt der einfachen Logik. Es geht um **simuliertes Verständnis** und situative Anpassung.

**Die technische Brücke:** Ich experimentiere hier mit der Kombination aus Vision-APIs und Sentiment-Analyse. Ein Screenshot oder eine Nachricht wird analysiert, um nicht nur Daten zu extrahieren, sondern die Intention des Nutzers zu begreifen.

**Das Gefühl:** Es gibt diesen Moment, wenn die KI eine Nuance erkennt, die nicht explizit codiert wurde. Software wird vom starren Werkzeug zum mitdenkenden Partner.`
  },
  {
    slug: 'typescript-zu-pydantic',
    title: 'Von TypeScript zu Pydantic: Meine Reise von deterministischer Software zu probabilistischer KI',
    publishedAt: new Date('2026-03-18'),
    tags: ['AI Engineering', 'Python', 'Pydantic', 'TypeScript'],
    excerpt:
      'Als Diplom-Informatiker begann mein Weg deterministisch: Objektorientierung, feste Verträge, vorhersehbare Systeme. Auf meinem aktuellen Weg in das AI Engineering stehe ich vor einem neuen Architektur-Bruch – und Pydantic ist die Brücke.',
    content: `Als Diplom-Informatiker begann mein Weg deterministisch: Objektorientierung, feste Verträge, vorhersehbare Systeme. Mit JavaScript und dem Prinzip des "Duck Typing" kam später die dynamische Freiheit in der Webentwicklung – und mit ihr kaskadierende Laufzeitfehler durch fehlende Typensicherheit. Die Industrie reagierte mit **TypeScript**: Compile-Time Safety brachte die Kontrolle zurück. Verträge im Code wurden wieder verlässlich.

Auf meinem aktuellen Weg in das AI Engineering mit Python stehe ich nun vor einem neuen Architektur-Bruch: Deterministische Kernsysteme (Datenbanken, APIs) kollidieren mit **probabilistischen** Large Language Models (LLMs).

Ein LLM kennt keine festen Datentypen; es generiert Fließtext auf Basis von Wahrscheinlichkeiten. Statische Compiler-Checks wie in TypeScript greifen hier ins Leere, da die Daten erst zur Laufzeit von der KI erzeugt (und potenziell halluziniert) werden. Wer unvalidierte LLM-Outputs blind in seine Systeme leitet, riskiert fatale Datenkorruption.

Die architektonische Brücke für dieses Problem heißt **Pydantic**. Es übersetzt Pythons statische Type Hints in eine unerbittliche Laufzeit-Validierung (Runtime Validation). Scheitert das LLM an dem definierten Daten-Schema, stürzt das System nicht ab. Pydantic wirft stattdessen eine strukturierte \`ValidationError\`. Diese nutze ich architektonisch, um sie als automatisierten Korrektur-Prompt an das Modell zurückzusenden (*Self-Correction Loop*).

**Fazit:** Die wichtigste Lektion aus der Evolution von JavaScript zu TypeScript bleibt bestehen: Robuste Systeme brauchen strikte Verträge. Pydantic ist dieser Vertrag für das KI-Zeitalter – es macht das Unberechenbare berechenbar.`
  },

].sort((a, b) => b.publishedAt.getTime() - a.publishedAt.getTime());
