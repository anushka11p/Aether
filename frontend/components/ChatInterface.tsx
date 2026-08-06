"use client";

import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

type StepMessage = { type: "step"; agent: string; iteration: number };
type DoneMessage = { type: "done"; final_output: string; iterations: number };

export default function ChatInterface() {
  const [task, setTask] = useState("");
  const [steps, setSteps] = useState<string[]>([]);
  const [finalOutput, setFinalOutput] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  const runTask = () => {
    if (!task.trim() || isRunning) return;

    setSteps([]);
    setFinalOutput(null);
    setIsRunning(true);

    const ws = new WebSocket("ws://127.0.0.1:8000/ws/run");
    wsRef.current = ws;

    ws.onopen = () => {
      ws.send(JSON.stringify({ task, api_key: process.env.NEXT_PUBLIC_AETHER_API_KEY }));
    };

    ws.onmessage = (event) => {
      const data: StepMessage | DoneMessage = JSON.parse(event.data);

      if (data.type === "step") {
        setSteps((prev) => [...prev, `${data.agent} (step ${data.iteration})`]);
      } else if (data.type === "done") {
        setFinalOutput(data.final_output);
        setIsRunning(false);
        ws.close();
      }
    };

    ws.onerror = () => {
      setIsRunning(false);
    };
  };

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-4">
      <h1 className="text-2xl font-bold">Aether</h1>

      <div className="flex gap-2">
        <Input
          value={task}
          onChange={(e) => setTask(e.target.value)}
          placeholder="Ask Aether something..."
          onKeyDown={(e) => e.key === "Enter" && runTask()}
          disabled={isRunning}
        />
        <Button onClick={runTask} disabled={isRunning}>
          {isRunning ? "Running..." : "Run"}
        </Button>
      </div>

      {steps.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {steps.map((s, i) => (
            <Badge key={i} variant="secondary">
              {s}
            </Badge>
          ))}
        </div>
      )}

      {finalOutput && (
        <Card>
          <CardContent className="pt-6 whitespace-pre-wrap">
            {finalOutput}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
