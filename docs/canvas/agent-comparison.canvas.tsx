import {
  Callout,
  Card,
  CardBody,
  CardHeader,
  Grid,
  H1,
  H2,
  H3,
  Pill,
  Stack,
  Stat,
  Table,
  Text,
  useHostTheme,
} from "cursor/canvas";

const REPO = "pallets/flask";

const DIMENSIONS: [string, string, string][] = [
  ["Data source", "GitHub API via get_repo_health", "None — guesses / stale training data"],
  ["Numeric context", "z-scores, historical averages, trends", "Raw counts or ungrounded estimates"],
  ["Tool calls", "get_repo_health + analyze_causal_patterns", "No tools invoked"],
  ["Causal claims", "Tier 2 + alternative explanation", "Unqualified assertions"],
  ["Confidence language", '"Based on observed patterns…"', '"Data proves…" / "Clearly declining"'],
];

const CAUSAL_SAMPLE = `Overview
pallets/flask — 72,163 stars, active maintenance with contextualized metrics.

Health Assessment
Recent weekly commits average 4.2 vs. a 52-week historical mean of 3.8
(z = +0.27 — within normal range). Top contributor share is 0.48.
Issue close ratio over 90d: 0.71.

Causal Analysis (Tier 2 — pattern match)
Release Drought pathway: last release 142 days ago — detected.
Alternative: intentional stability in a mature API.

Assessment
Activity is healthy on self-history benchmarks. Release cadence is slow
but may reflect stability rather than abandonment.`;

const NAIVE_SAMPLE = `Flask is a popular Python web framework with around 65,000 stars
and strong community support. Commit activity appears steady and the
project is well maintained. Maintainer burnout may be a concern.
Overall Flask looks like a healthy choice for production use.`;

const TOOL_TRACE = [
  "[Calling get_repo_health({'owner': 'pallets', 'repo': 'flask'})]",
  "[Calling analyze_causal_patterns({'owner': 'pallets', 'repo': 'flask'})]",
];

export default function AgentComparisonCanvas() {
  const theme = useHostTheme();

  return (
    <Stack gap={20} style={{ padding: 24, maxWidth: 1100 }}>
      <Stack gap={6}>
        <H1>Causal vs Naive Agent</H1>
        <Text tone="secondary">
          Workshop wrap-up — compare your terminal output from{" "}
          <InlineCode theme={theme}>uv run src/agent.py</InlineCode> against this rubric.
          {" "}Source: {REPO} · illustrative samples below.
        </Text>
      </Stack>

      <Grid columns={4} gap={12}>
        <Stat label="Causal tool calls" value="2" tone="success" />
        <Stat label="Naive tool calls" value="0" tone="danger" />
        <Stat label="Evidence tier stated" value="Yes" tone="success" />
        <Stat label="Alternative cited" value="Yes" tone="success" />
      </Grid>

      <Stack gap={8}>
        <H2>What to look for</H2>
        <Table
          headers={["Dimension", "Causal agent", "Naive agent"]}
          rows={DIMENSIONS}
          striped
        />
      </Stack>

      <Grid columns={2} gap={16}>
        <Card>
          <CardHeader trailing={<Pill tone="success">tools + rules</Pill>}>
            Causal agent
          </CardHeader>
          <CardBody>
            <Stack gap={12}>
              <Stack gap={6}>
                <H3>Terminal trace</H3>
                <Text
                  tone="secondary"
                  size="small"
                  style={{ fontFamily: "monospace", whiteSpace: "pre-wrap" }}
                >
                  {TOOL_TRACE.join("\n")}
                </Text>
              </Stack>
              <Stack gap={6}>
                <H3>Sample narrative (abbreviated)</H3>
                <Text style={{ whiteSpace: "pre-wrap", lineHeight: 1.5 }}>{CAUSAL_SAMPLE}</Text>
              </Stack>
            </Stack>
          </CardBody>
        </Card>

        <Card>
          <CardHeader trailing={<Pill tone="warning">no tools</Pill>}>
            Naive agent
          </CardHeader>
          <CardBody>
            <Stack gap={12}>
              <Stack gap={6}>
                <H3>Terminal trace</H3>
                <Text tone="tertiary" size="small" style={{ fontFamily: "monospace" }}>
                  (no tool calls)
                </Text>
              </Stack>
              <Stack gap={6}>
                <H3>Sample narrative (abbreviated)</H3>
                <Text style={{ whiteSpace: "pre-wrap", lineHeight: 1.5 }}>{NAIVE_SAMPLE}</Text>
              </Stack>
            </Stack>
          </CardBody>
        </Card>
      </Grid>

      <Callout tone="info" title="Your turn">
        Run <InlineCode theme={theme}>uv run src/agent.py</InlineCode> from the project root.
        Read both sections in your terminal. Which agent would you trust for an adoption decision?
      </Callout>
    </Stack>
  );
}

function InlineCode({
  children,
  theme,
}: {
  children: string;
  theme: ReturnType<typeof useHostTheme>;
}) {
  return (
    <span
      style={{
        fontFamily: "monospace",
        fontSize: 12,
        padding: "2px 6px",
        borderRadius: 4,
        background: theme.fill.secondary,
        color: theme.text.primary,
      }}
    >
      {children}
    </span>
  );
}
