import React, { useState, useEffect } from "react";
import axios from "axios";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";

const AnalysisTool = () => {
  const [token, setToken] = useState("");
  const [countries, setCountries] = useState(["USA"]);
  const [startYear, setStartYear] = useState(2000);
  const [endYear, setEndYear] = useState(2020);
  const [dependentMetric, setDependentMetric] = useState("GDP");
  const [baseMetric, setBaseMetric] = useState("Bank_Credit");
  const [controlMetrics, setControlMetrics] = useState(["Inflation"]);
  const [method, setMethod] = useState("OLS");
  const [previewData, setPreviewData] = useState(null);
  const [uploadedDatasetId, setUploadedDatasetId] = useState("");
  const [userDatasets, setUserDatasets] = useState([]);
  const [uploadFile, setUploadFile] = useState(null);
  const [result, setResult] = useState(null);

  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    if (token) {
      axios.get("/my-datasets/", { headers }).then((res) => setUserDatasets(res.data));
    }
  }, [token]);

  const handlePreview = async () => {
    const res = await axios.post("/run-analysis/", {
      countries,
      method,
      dependent_metric: dependentMetric,
      base_metric: baseMetric,
      control_metrics: controlMetrics,
      start_year: startYear,
      end_year: endYear,
      uploaded_dataset_id: uploadedDatasetId,
      preview: true
    }, { headers });
    setPreviewData(res.data);
  };

  const handleRunAnalysis = async () => {
    const res = await axios.post("/run-analysis/", {
      countries,
      method,
      dependent_metric: dependentMetric,
      base_metric: baseMetric,
      control_metrics: controlMetrics,
      start_year: startYear,
      end_year: endYear,
      uploaded_dataset_id: uploadedDatasetId
    }, { headers });
    setResult(res.data);
  };

  const handleUpload = async () => {
    const formData = new FormData();
    formData.append("file", uploadFile);
    const res = await axios.post("/upload-dataset/", formData, { headers });
    alert("Файл загружен");
    setUploadedDatasetId(res.data.dataset_id);
    const ds = await axios.get("/my-datasets/", { headers });
    setUserDatasets(ds.data);
  };

  return (
    <div className="p-4 space-y-4">
      <Card>
        <CardContent className="space-y-2">
          <Input placeholder="Token" value={token} onChange={(e) => setToken(e.target.value)} />
          <Input placeholder="Страны (через запятую)" value={countries.join(",")} onChange={(e) => setCountries(e.target.value.split(","))} />
          <Input placeholder="Start Year" type="number" value={startYear} onChange={(e) => setStartYear(+e.target.value)} />
          <Input placeholder="End Year" type="number" value={endYear} onChange={(e) => setEndYear(+e.target.value)} />
          <Input placeholder="Dependent Metric" value={dependentMetric} onChange={(e) => setDependentMetric(e.target.value)} />
          <Input placeholder="Base Metric" value={baseMetric} onChange={(e) => setBaseMetric(e.target.value)} />
          <Input placeholder="Control Metrics (через запятую)" value={controlMetrics.join(",")} onChange={(e) => setControlMetrics(e.target.value.split(","))} />
          <input type="file" onChange={(e) => setUploadFile(e.target.files[0])} />
          <Button onClick={handleUpload} disabled={!uploadFile}>Загрузить файл</Button>

          <Select value={uploadedDatasetId} onValueChange={setUploadedDatasetId}>
            <SelectTrigger><SelectValue placeholder="Выбери загруженный датасет" /></SelectTrigger>
            <SelectContent>
              {userDatasets.map((ds) => (
                <SelectItem key={ds.dataset_id} value={ds.dataset_id}>{ds.file_name}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={method} onValueChange={setMethod}>
            <SelectTrigger><SelectValue placeholder="Метод" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="OLS">OLS</SelectItem>
              <SelectItem value="2SLS">2SLS</SelectItem>
              <SelectItem value="FE">Fixed Effects</SelectItem>
              <SelectItem value="RE">Random Effects</SelectItem>
            </SelectContent>
          </Select>

          <div className="flex space-x-2">
            <Button onClick={handlePreview}>Предпросмотр объединения</Button>
            <Button onClick={handleRunAnalysis}>Запуск анализа</Button>
          </div>
        </CardContent>
      </Card>

      {previewData && (
        <Card>
          <CardContent>
            <div className="text-lg font-bold mb-2">Превью объединённых данных</div>
            <pre className="overflow-auto text-sm">{JSON.stringify(previewData, null, 2)}</pre>
          </CardContent>
        </Card>
      )}

      {result && (
        <Card>
          <CardContent>
            <div className="text-lg font-bold mb-2">Результат анализа</div>
            <pre className="overflow-auto text-sm">{JSON.stringify(result, null, 2)}</pre>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default AnalysisTool;
