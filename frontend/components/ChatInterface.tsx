"use client";

import { useRef, useState } from "react";

type StepMessage = {
  type: "step";
  agent: string;
  iteration: number;
};

type DoneMessage = {
  type: "done";
  final_output: string;
  iterations: number;
};

type ErrorMessage = {
  type: "error";
  message: string;
};

type ServerMessage = StepMessage | DoneMessage | ErrorMessage;

const AGENT_LABELS: Record<string, string> = {
  researcher: "researching",
  writer: "writing",
  coder: "writing code",
  critic: "reviewing",
};

// 0 = transparent
// 1 = light body
// 2 = mid body
// 3 = dark body / outline
// 4 = blush
// 5 = eye / mouth dark
// 6 = mouth pink

const BLOB_GRID = [
  [0, 0, 0, 0, 3, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0],
  [0, 0, 0, 3, 1, 1, 1, 1, 1, 1, 1, 1, 3, 0, 0, 0],
  [0, 0, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 0, 0],
  [0, 3, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 3, 0],
  [0, 3, 1, 2, 2, 5, 5, 1, 1, 5, 5, 2, 2, 1, 3, 0],
  [3, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 3],
  [3, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 3],
  [3, 1, 4, 4, 2, 1, 1, 1, 1, 1, 1, 2, 4, 4, 1, 3],
  [3, 1, 4, 4, 2, 1, 1, 6, 6, 1, 1, 2, 4, 4, 1, 3],
  [3, 1, 1, 2, 2, 1, 6, 5, 5, 6, 1, 2, 2, 1, 1, 3],
  [0, 3, 1, 2, 2, 1, 1, 1, 1, 1, 1, 2, 2, 1, 3, 0],
  [0, 3, 1, 1, 2, 2, 1, 1, 1, 1, 2, 2, 1, 1, 3, 0],
  [0, 0, 3, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 3, 0, 0],
  [0, 0, 0, 3, 1, 1, 1, 1, 1, 1, 1, 1, 3, 0, 0, 0],
  [0, 0, 0, 0, 3, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0],
];

const PALETTE: Record<number, string> = {
  1: "#c9f0c9",
  2: "#8fd48f",
  3: "#3f6b3f",
  4: "#f6b9c4",
  5: "#2e3a2e",
  6: "#e0607a",
};

function BlobMascot() {
  const cell = 7;

  return (
    <div className="flex items-end gap-5 mb-10">
      {/* Mascot */}
      <div
        className="relative shrink-0"
        style={{
          width: 125,
          height: 135,
        }}
      >
        {/* Pixel shadow */}
        <div
          className="absolute left-1/2 bottom-0"
          style={{
            width: 68,
            height: 12,
            marginLeft: -34,
            background: "#c9532e",
            opacity: 0.22,
            animation: "blob-shadow 1.15s steps(6) infinite",
          }}
        />

        {/* Blob */}
        <div
          className="absolute left-1/2 bottom-4"
          style={{
            marginLeft: -(cell * 16) / 2,
            animation: "blob-jump 1.15s steps(6) infinite",
            transformOrigin: "bottom center",
            imageRendering: "pixelated",
          }}
        >
          <div
            style={{
              display: "grid",
              gridTemplateColumns: `repeat(16, ${cell}px)`,
              gridTemplateRows: `repeat(15, ${cell}px)`,
            }}
          >
            {BLOB_GRID.flatMap((row, y) =>
              row.map((v, x) => (
                <div
                  key={`${x}-${y}`}
                  style={{
                    width: cell,
                    height: cell,
                    background: v === 0 ? "transparent" : PALETTE[v],
                  }}
                />
              ))
            )}
          </div>
        </div>
      </div>

      {/* Speech bubble */}
      <div
        className="relative px-5 py-4 pixel-font"
        style={{
          background: "#f4ead5",
          border: "3px solid #171b17",
          color: "#171b17",
          maxWidth: 310,
          marginBottom: 42,
          fontSize: "9px",
          lineHeight: 1.9,
          boxShadow: "5px 5px 0 rgba(20, 25, 20, 0.3)",
          imageRendering: "pixelated",
        }}
      >
        Ask Aether anything. She and her team will get you the answers,
        they&rsquo;re all very smart.

        {/* Pixel speech tail */}
        <div
          className="absolute"
          style={{
            left: -11,
            bottom: 16,
            width: 14,
            height: 14,
            background: "#f4ead5",
            borderLeft: "3px solid #171b17",
            borderBottom: "3px solid #171b17",
          }}
        />
      </div>
    </div>
  );
}

export default function ChatInterface() {
  const [task, setTask] = useState("");
  const [steps, setSteps] = useState<string[]>([]);
  const [finalOutput, setFinalOutput] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  const wsRef = useRef<WebSocket | null>(null);

  const runTask = () => {
    if (!task.trim() || isRunning) return;

    setSteps([]);
    setFinalOutput(null);
    setError(null);
    setIsRunning(true);

    const ws = new WebSocket("ws://127.0.0.1:8000/ws/run");

    wsRef.current = ws;

    const key = process.env.NEXT_PUBLIC_AETHER_API_KEY || "";

    ws.onopen = () => {
      ws.send(
        JSON.stringify({
          task,
          api_key: key,
        })
      );
    };

    ws.onmessage = (event) => {
      const data: ServerMessage = JSON.parse(event.data);

      if (data.type === "step") {
        setSteps((prev) => [
          ...prev,
          AGENT_LABELS[data.agent] || data.agent,
        ]);
      } else if (data.type === "done") {
        setFinalOutput(data.final_output);
        setIsRunning(false);
        ws.close();
      } else if (data.type === "error") {
        setError(data.message);
        setIsRunning(false);
        ws.close();
      }
    };

    ws.onerror = () => {
      setError("Could not reach the server.");
      setIsRunning(false);
    };

    ws.onclose = () => {
      setIsRunning(false);
    };
  };

  return (
    <div
      className="min-h-screen"
      style={{
        backgroundImage: "url('/background.png')",
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundAttachment: "fixed",
        imageRendering: "pixelated",
      }}
    >
      {/* Dark atmospheric overlay */}
      <div
        className="min-h-screen"
        style={{
          background: "rgba(31, 37, 34, 0.48)",
          position: "relative",
        }}
      >
        {/* Subtle pixel atmosphere */}
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            background:
              "linear-gradient(to bottom, rgba(20,25,22,0.10), rgba(20,25,22,0.28))",
          }}
        />

        {/* Main content */}
        <div
          className="relative max-w-xl mx-auto px-6 pt-20 pb-32"
          style={{
            zIndex: 1,
          }}
        >
          {/* Title */}
          <h1
            className="pixel-font mb-4"
            style={{
              fontSize: "28px",
              lineHeight: 1.2,
              color: "#172019",
              letterSpacing: "1px",
              textShadow: "2px 2px 0 rgba(244, 234, 213, 0.45)",
            }}
          >
            AETHER
          </h1>

          {/* Subtitle */}
          <p
            className="pixel-font mb-10"
            style={{
              fontSize: "8px",
              lineHeight: 2,
              color: "#172019",
              maxWidth: 480,
              textShadow: "1px 1px 0 rgba(244, 234, 213, 0.4)",
            }}
          >
            A small council of agents that researches, writes, and checks its
            own work.
          </p>

          {/* Mascot */}
          <BlobMascot />

          {/* Input / button */}
          <div
            className="flex items-stretch gap-0 mb-2"
            style={{
              filter: "drop-shadow(5px 5px 0 rgba(20, 25, 20, 0.25))",
            }}
          >
            <input
              value={task}
              onChange={(e) => setTask(e.target.value)}
              placeholder="Ask it something"
              onKeyDown={(e) => {
                if (e.key === "Enter") runTask();
              }}
              disabled={isRunning}
              className="flex-1 px-5 py-4 outline-none pixel-font"
              style={{
                background: "#f4ead5",
                border: "3px solid #171b17",
                borderRight: "0",
                color: "#171b17",
                fontSize: "9px",
                minWidth: 0,
                imageRendering: "pixelated",
              }}
            />

            <button
              onClick={runTask}
              disabled={isRunning}
              className="px-6 py-4 pixel-font"
              style={{
                background: isRunning ? "#c7bfae" : "#252b25",
                color: isRunning ? "#665f50" : "#f4ead5",
                border: "3px solid #171b17",
                cursor: isRunning ? "default" : "pointer",
                fontSize: "9px",
                minWidth: 92,
                imageRendering: "pixelated",
              }}
            >
              {isRunning ? "WORKING" : "RUN"}
            </button>
          </div>

          {/* Agent activity */}
          {steps.length > 0 && (
            <div
              className="mt-10 pixel-font"
              style={{
                color: "#172019",
                fontSize: "9px",
                lineHeight: 2.5,
                letterSpacing: "0.3px",
                textShadow: "1px 1px 0 rgba(244, 234, 213, 0.35)",
              }}
            >
              {steps.map((s, i) => (
                <div key={i}>
                  <span
                    style={{
                      color: "#d85b32",
                      marginRight: 8,
                    }}
                  >
                    ›
                  </span>

                  {s}

                  {i === steps.length - 1 && isRunning ? " ..." : ""}
                </div>
              ))}
            </div>
          )}

          {/* Error */}
          {error && (
            <div
              className="mt-8 pixel-font"
              style={{
                color: "#c94d35",
                fontSize: "9px",
                lineHeight: 2,
              }}
            >
              › {error}
            </div>
          )}

          {/* Final answer */}
          {finalOutput && (
            <div
              className="mt-10 pt-8 pixel-font whitespace-pre-wrap"
              style={{
                borderTop: "3px solid #171b17",
                color: "#172019",
                fontSize: "9px",
                lineHeight: 2,
                textShadow: "1px 1px 0 rgba(244, 234, 213, 0.4)",
              }}
            >
              {finalOutput}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}