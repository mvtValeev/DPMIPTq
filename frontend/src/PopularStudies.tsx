import React, { useEffect, useState } from "react";
import axios from "axios";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const PopularStudies = () => {
  const [studies, setStudies] = useState([]);

  useEffect(() => {
    axios.get("/popular-studies/").then((res) => setStudies(res.data));
  }, []);

  return (
    <div className="p-4 space-y-4">
      {studies.map((study, idx) => (
        <Card key={idx}>
          <CardContent>
            <div className="font-bold">Метод: {study.method}</div>
            <div>Зависимая: {study.dependent_metric}</div>
            <div>Базовая: {study.base_metric}</div>
            <div>Контрольные: {study.control_metrics?.join(", ")}</div>
            <div>Повторов: {study.count}</div>
            <Button
              onClick={() => navigator.clipboard.writeText(JSON.stringify(study, null, 2))}
              className="mt-2"
            >
              Скопировать параметры
            </Button>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

export default PopularStudies;
