import { useMemo, useState } from "react";
import { Background, Handle, MarkerType, Position, ReactFlow } from "@xyflow/react";
import IconAlertTriangle from "@tabler/icons-react/dist/esm/icons/IconAlertTriangle.mjs";
import IconCheck from "@tabler/icons-react/dist/esm/icons/IconCheck.mjs";
import IconDatabase from "@tabler/icons-react/dist/esm/icons/IconDatabase.mjs";
import IconLayoutDashboard from "@tabler/icons-react/dist/esm/icons/IconLayoutDashboard.mjs";
import IconLayersLinked from "@tabler/icons-react/dist/esm/icons/IconLayersLinked.mjs";
import IconLock from "@tabler/icons-react/dist/esm/icons/IconLock.mjs";

/** @typedef {typeof import("../data/caseData.js").caseData} CaseData */
/** @typedef {CaseData["graph"]["nodes"][number]} GraphNode */
/** @typedef {import("../hooks/useForgetOpsWorkflow.js").StageId} StageId */
/** @typedef {"legal-hold" | "manual-review" | "executing" | "verified" | "planned"} NodeVisualState */
/**
 * @typedef {{
 *   asset: GraphNode;
 *   state: NodeVisualState;
 *   label: string;
 *   select: (id: string) => void;
 * }} AssetNodeData
 */

/** @type {Record<string, { x: number; y: number }>} */
const POSITIONS = {
  "asset-01": { x: 192, y: 16 },
  "asset-02": { x: 8, y: 138 },
  "asset-03": { x: 192, y: 154 },
  "asset-04": { x: 376, y: 304 },
  "asset-05": { x: 376, y: 154 },
  "asset-06": { x: 8, y: 304 },
  "asset-07": { x: 192, y: 322 },
};

/** @type {Record<string, string>} */
const DISPLAY_NAMES = {
  "ecommerce.customers": "Ecommerce customers",
  "support.tickets": "Support tickets",
  "analytics.customer_360": "Customer 360",
  "Customer Retention Overview": "Retention overview",
  "finance.invoices": "Finance invoices",
  "marketing.customer_export": "Marketing export",
  "ml.customer_churn_features": "Churn features",
};

/** @param {GraphNode} node */
function displayName(node) {
  return DISPLAY_NAMES[node.name] ?? node.name.replaceAll(/[._]/g, " ");
}

/**
 * @param {GraphNode} node
 * @param {StageId} phase
 * @returns {NodeVisualState}
 */
function nodeState(node, phase) {
  if (node.exceptionType === "legal_hold") return "legal-hold";
  if (node.exceptionType === "manual_review") return "manual-review";
  if (phase === "execute") return "executing";
  if (phase === "verify" || phase === "remember") return "verified";
  return "planned";
}

/** @param {{ kind: string; state: NodeVisualState }} props */
function NodeIcon({ kind, state }) {
  if (state === "legal-hold") return <IconLock aria-hidden="true" size={14} />;
  if (state === "manual-review") {
    return <IconAlertTriangle aria-hidden="true" size={14} />;
  }
  if (state === "verified") return <IconCheck aria-hidden="true" size={14} />;
  if (kind === "dashboard") {
    return <IconLayoutDashboard aria-hidden="true" size={14} />;
  }
  return <IconDatabase aria-hidden="true" size={14} />;
}

/**
 * @param {import("@xyflow/react").NodeProps<import("@xyflow/react").Node<AssetNodeData, "asset">>} props
 */
function AssetNode({ data }) {
  return (
    <div className="flow-node-shell">
      <Handle type="target" position={Position.Top} />
      <button
        className="asset-node"
        data-state={data.state}
        type="button"
        onClick={() => data.select(data.asset.id)}
        aria-label={`${data.asset.name}, ${data.label}`}
      >
        <span className="asset-node-index">{data.asset.id.slice(-2)}</span>
        <span className="asset-node-copy">
          <strong>{displayName(data.asset)}</strong>
          <small>
            {data.asset.platform} · {data.asset.owners.join(", ")}
          </small>
        </span>
        <NodeIcon kind={data.asset.kind} state={data.state} />
      </button>
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

/** @type {import("@xyflow/react").NodeTypes} */
const nodeTypes = { asset: AssetNode };

/**
 * @param {GraphNode} node
 * @param {StageId} phase
 */
function stateLabel(node, phase) {
  const state = nodeState(node, phase);
  if (state === "legal-hold") return "Retained: legal hold";
  if (state === "manual-review") return "Manual review: not modified";
  if (state === "executing") return "Mutation receipt pending";
  if (state === "verified") return "Verified permitted outcome";
  return "Scheduled for safe mutation";
}

/** @param {{ data: CaseData; phase: StageId }} props */
export function ImpactMap({ data, phase }) {
  const [selectedNodeId, setSelectedNodeId] = useState(/** @type {string | null} */ (null));

  const nodes = useMemo(
    () =>
      data.graph.nodes.map((asset) => ({
        id: asset.id,
        type: "asset",
        position: POSITIONS[asset.id] ?? { x: 0, y: 0 },
        draggable: false,
        selectable: false,
        data: {
          asset,
          state: nodeState(asset, phase),
          label: stateLabel(asset, phase),
          select: setSelectedNodeId,
        },
      })),
    [data.graph.nodes, phase],
  );

  const edges = useMemo(
    () =>
      data.graph.edges.map((edge) => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        type: "smoothstep",
        markerEnd: {
          type: MarkerType.ArrowClosed,
          width: 13,
          height: 13,
          color: "var(--flow-edge)",
        },
        style: { stroke: "var(--flow-edge)", strokeWidth: 1.25 },
        animated: phase === "execute",
      })),
    [data.graph.edges, phase],
  );

  const selected = selectedNodeId
    ? data.graph.nodes.find((node) => node.id === selectedNodeId)
    : null;

  return (
    <section className="impact-map" aria-labelledby="impact-map-title">
      <header className="impact-map-header">
        <div>
          <span className="section-kicker">Impact map</span>
          <h2 id="impact-map-title">
            {data.metrics.assets} assets discovered · {data.metrics.lineageEdges} lineage edges
          </h2>
        </div>
        <strong>Owner coverage: {data.metrics.ownerCoveragePct}%</strong>
      </header>
      <p className="provenance-line">
        <IconLayersLinked aria-hidden="true" size={17} stroke={1.8} />
        Provenance: DataHub
      </p>

      <div className="flow-map" role="group" aria-label="DataHub lineage impact graph">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{ padding: 0.04, minZoom: 0.5, maxZoom: 0.9 }}
          minZoom={0.5}
          maxZoom={0.92}
          nodesDraggable={false}
          nodesConnectable={false}
          elementsSelectable={false}
          panOnDrag={false}
          zoomOnScroll={false}
          zoomOnPinch={false}
          zoomOnDoubleClick={false}
          preventScrolling={false}
          proOptions={{ hideAttribution: true }}
        >
          <Background color="var(--flow-grid)" gap={24} size={1} />
        </ReactFlow>
      </div>

      <ol className="mobile-asset-list" aria-label="Affected DataHub assets">
        {data.graph.nodes.map((node) => (
          <li key={node.id} data-state={nodeState(node, phase)}>
            <span>{node.id.slice(-2)}</span>
            <div>
              <strong>{displayName(node)}</strong>
              <small>{node.owners.join(", ")}</small>
            </div>
            <em>{stateLabel(node, phase)}</em>
          </li>
        ))}
      </ol>

      <div className="impact-map-footer">
        <ul className="graph-legend" aria-label="Impact map legend">
          <li data-state="planned">Scheduled for safe mutation ({data.metrics.safeMutations})</li>
          <li data-state="legal-hold">Retained: legal hold ({data.metrics.legalHolds})</li>
          <li data-state="manual-review">
            Manual review: not modified ({data.metrics.manualReviews})
          </li>
        </ul>
        <div className="graph-proof" aria-live="polite">
          <IconLayersLinked aria-hidden="true" size={22} stroke={1.8} />
          {selected ? (
            <span>
              <strong>{selected.name}</strong>
              {selected.policySource}
            </span>
          ) : (
            <span>
              <strong>Lineage &amp; ownership from DataHub</strong>
              Verified snapshot {data.meta.graphSnapshotId}
            </span>
          )}
        </div>
      </div>
    </section>
  );
}
