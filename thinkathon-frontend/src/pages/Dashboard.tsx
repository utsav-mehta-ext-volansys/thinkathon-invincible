import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { Header } from "@/components/Header";
import { 
  Upload, 
  FileText, 
  Activity, 
  Heart, 
  TrendingUp, 
  AlertTriangle,
  CheckCircle,
  Download,
  Calendar,
  User
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { useNavigate } from "react-router-dom";

// Mock patient data
// const patientData = {
//   name: "John Doe",
//   age: 35,
//   lastUpdate: "2024-01-15",
//   tests: [
//     {
//       name: "Complete Blood Count (CBC)",
//       date: "2024-01-15",
//       status: "normal",
//       values: {
//         "White Blood Cells": { value: "7.2", unit: "K/μL", range: "4.0-11.0", status: "normal" },
//         "Red Blood Cells": { value: "4.8", unit: "M/μL", range: "4.2-5.8", status: "normal" },
//         "Hemoglobin": { value: "14.5", unit: "g/dL", range: "13.5-17.5", status: "normal" },
//         "Hematocrit": { value: "42.1", unit: "%", range: "38.0-50.0", status: "normal" },
//         "Platelets": { value: "280", unit: "K/μL", range: "150-450", status: "normal" }
//       },
//       recommendation: "Your blood count is within normal ranges. Continue your current health routine."
//     },
//     {
//       name: "Blood Pressure",
//       date: "2024-01-15",
//       status: "warning",
//       values: {
//         "Systolic": { value: "135", unit: "mmHg", range: "<120", status: "high" },
//         "Diastolic": { value: "88", unit: "mmHg", range: "<80", status: "high" }
//       },
//       recommendation: "Your blood pressure is elevated. Consider reducing sodium intake and consult your doctor."
//     },
//     {
//       name: "Lipid Panel",
//       date: "2024-01-10",
//       status: "critical",
//       values: {
//         "Total Cholesterol": { value: "240", unit: "mg/dL", range: "<200", status: "high" },
//         "LDL Cholesterol": { value: "165", unit: "mg/dL", range: "<100", status: "high" },
//         "HDL Cholesterol": { value: "42", unit: "mg/dL", range: ">40", status: "normal" },
//         "Triglycerides": { value: "185", unit: "mg/dL", range: "<150", status: "high" }
//       },
//       recommendation: "High cholesterol levels detected. Schedule an appointment with your doctor immediately to discuss treatment options."
//     }
//   ]
// };

export default function Dashboard() {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [showResults, setShowResults] = useState(false); // Show mock data by default
  const [patientData, setPatientData] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const { toast } = useToast();
  const navigate = useNavigate();


  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

const handleUploadSubmit = async () => {
  if (!file) {
    toast({
      title: "No file selected",
      description: "Please select a CSV or Excel file to upload.",
      variant: "destructive",
    });
    return;
  }

  setIsUploading(true);
  setShowResults(false);
  setUploadProgress(0);

  // Fake progress updater
  const progressInterval = setInterval(() => {
    setUploadProgress((oldProgress) => {
      if (oldProgress >= 90) {
        return oldProgress;
      }
      return oldProgress + 10;
    });
  }, 900);

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch("http://localhost:8000/api/upload", {
      method: "POST",
      body: formData,
    });

    clearInterval(progressInterval);
    setUploadProgress(100); // Upload complete

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "File processing failed.");
    }

    const result = await response.json();
    console.log("Processed result:", result.data);
    
    setPatientData(result.data);

    setShowResults(true);
    toast({
      title: "Analysis Complete!",
      description: "Your health data has been processed and analyzed.",
    });
  } catch (error: any) {
    clearInterval(progressInterval);
    setUploadProgress(0);

    console.error("Upload error:", error);
    toast({
      title: "Upload Failed",
      description: error.message || "Something went wrong.",
      variant: "destructive",
    });
  } finally {
    setIsUploading(false);
  }
};


  const getStatusColor = (status: string) => {
    switch (status) {
      case "normal": return "text-health-normal";
      case "warning": return "text-health-warning";
      case "critical": return "text-health-critical";
      case "high": return "text-health-critical";
      default: return "text-foreground";
    }
  };

  const getStatusBg = (status: string) => {
    switch (status) {
      case "normal": return "bg-health-normal/10 border-health-normal/20";
      case "warning": return "bg-health-warning/10 border-health-warning/20";
      case "critical": return "bg-health-critical/10 border-health-critical/20";
      default: return "bg-muted";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "normal": return <CheckCircle className="h-5 w-5 text-health-normal" />;
      case "warning": return <AlertTriangle className="h-5 w-5 text-health-warning" />;
      case "critical": return <AlertTriangle className="h-5 w-5 text-health-critical" />;
      default: return <Activity className="h-5 w-5" />;
    }
  };

  const handleDownload = () => {
    if (!patientData || !patientData.tests) {
      alert("No data available to export.");
      return;
    }

    const rows = [];

    // Optional: Add user info as first row
    rows.push(["Name", "Age", "ReportDate"]);
    rows.push([
      patientData.Name || "",
      patientData.Age || "",
      patientData.ReportDate || "",
    ]);
    rows.push([]); // blank row for spacing

    // Add headers for tests
    patientData.tests.forEach((test) => {
      rows.push([`Test: ${test.name}`]);
      rows.push(["Parameter", "Value"]);
      Object.entries(test.values).forEach(([param, value]) => {
        rows.push([param, value]);
      });
      rows.push(["Recommendation", `"${test.recommendation}"`]);
      rows.push([]); // spacing between tests
    });

    // Convert to CSV string
    const csvContent = rows.map((row) => row.join(",")).join("\n");

    // Create a blob and download link
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "health_report.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };


  return (
    <div className="min-h-screen bg-background">
      <Header isAuthenticated={true} onLogout={() => navigate("/")} />
      
      <div className="container mx-auto px-4 py-8 space-y-8">
        {/* Welcome Section */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Health Dashboard</h1>
            <p className="text-muted-foreground">Monitor your health metrics and get personalized insights</p>
          </div>
          {/* <div className="flex items-center space-x-2 text-sm text-muted-foreground">
            <Calendar className="h-4 w-4" />
            <span>Last updated: {patientData && patientData?.lastUpdate}</span>
          </div> */}
        </div>

        {/* Upload Section */}
        {!showResults && (
          <Card className="border-2 border-dashed border-primary/20 bg-gradient-hero">
            <CardHeader className="text-center">
              <CardTitle className="flex items-center justify-center space-x-2">
                <Upload className="h-6 w-6" />
                <span>Upload Your Health Data</span>
              </CardTitle>
              <p className="text-muted-foreground">
                Upload a CSV file containing your lab results, vitals, or health metrics
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="csv-file">Select CSV File</Label>
                <Input
                  id="csv-file"
                  type="file"
                  accept=".csv"
                  onChange={handleFileUpload}
                  className="cursor-pointer"
                />
              </div>
              
              {file && (
                <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                  <FileText className="h-4 w-4" />
                  <span>{file.name}</span>
                  <span>({(file.size / 1024).toFixed(1)} KB)</span>
                </div>
              )}

              <Button 
                onClick={handleUploadSubmit}
                disabled={!file || isUploading}
                className="w-full bg-gradient-medical shadow-medical"
              >
                {isUploading ? (
                  <>
                    <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Upload className="mr-2 h-4 w-4" />
                    Analyze Health Data
                  </>
                )}
              </Button>

              {isUploading && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Processing your data...</span>
                    <span>{uploadProgress}%</span>
                  </div>
                  <Progress value={uploadProgress} className="h-2" />
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Results Section */}
        {showResults && (
          <div className="space-y-6">
            {/* Patient Info */}
            <Card className="shadow-card-hover">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <User className="h-5 w-5" />
                  <span>Patient Information</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-3 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Name</p>
                    <p className="font-semibold">{patientData && patientData?.Name}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Age</p>
                    <p className="font-semibold">{patientData && patientData?.Age} years</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Last Test</p>
                    <p className="font-semibold">{patientData?.ReportDate}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Health Tests */}
            <div className="space-y-6">
              {patientData && patientData?.tests?.map((test: any, index: any) => (
                <Card 
                  key={index} 
                  className={`shadow-card-hover border-l-4 ${getStatusBg(test.status)} animate-fade-in`}
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(test.status)}
                        <span>{test.name}</span>
                      </div>
                      <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                        <Calendar className="h-4 w-4" />
                        <span>{test.date}</span>
                      </div>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* Test Values */}
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {Object.entries(test.values).map(([key, value]: any) => (
  <div key={key} className="space-y-1">
    <p className="text-sm font-medium">{key}</p>
    <div className="flex items-center justify-between">
      <span className={`text-lg font-bold ${getStatusColor(value.status)}`}>
        {value.value}
      </span>
      {/* Optionally display range here if you want */}
      {/* <span className="text-xs text-muted-foreground">Normal: {val.range}</span> */}
    </div>
  </div>
))}
                    </div>

                    {/* Recommendation */}
                    <div className={`p-4 rounded-lg ${getStatusBg(test.status)}`}>
                      <div className="flex items-start space-x-2">
                        <Heart className="h-5 w-5 mt-0.5 text-primary" />
                        <div>
                          <p className="font-semibold text-sm mb-1">Recommendation</p>
                          <p className="text-sm">{test.recommendation}</p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 pt-6">
              {showResults && <Button className="bg-gradient-medical shadow-medical" onClick={() => handleDownload()} >
                <Download className="mr-2 h-4 w-4"/>
                Download Report
              </Button>
              }
              <Button 
                variant="outline"
                onClick={() => setShowResults(false)}
              >
                <Upload className="mr-2 h-4 w-4" />
                Upload New Data
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}