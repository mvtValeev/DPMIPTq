import React, { useEffect, useState } from "react";
import axios from "axios";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

const History = () => {
  const [token, setToken] = useState("");
  const [history, setHistory] = useState([]);

  const fetchHistory = async () => {
    const res = await axios.get("/my-studies/", {
      headers: { Authorization: `Bearer ${token}` }
    });
    setHistory(res.data);
  };

  return (
    <div className="p-4 space-y-4">
      <Card>
        <CardContent className="space-y-2">
          <Input
            placeholder="Token для истории"
            value={token}
            onChange={(e) => setToken(e.target.value)}
          />
          <Button onClick={fetchHistory}>Загрузить историю</Button>
        </CardContent>
      </Card>

      {history.map((item, idx) => (
        <Card key={idx}>
          <CardContent>
            <div className="font-bold">Метод: {item.method}</div>
            <div>Период: {item.start_year}–{item.end_year}</div>
            <div>Страны: {item.countries.join(", ")}</div>
            <div>Метрики: {item.metrics.join(", ")}</div>
            <div>R²: {item.r_squared}</div>
            <pre className="text-sm overflow-auto mt-2">{item.summary}</pre>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

export default History;
