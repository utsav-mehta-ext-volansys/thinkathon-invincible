import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Heart, Shield, TrendingUp, Users } from "lucide-react";
import { useNavigate } from "react-router-dom";

export const HeroSection = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: Heart,
      title: "Health Monitoring",
      description: "Track vital signs, lab results, and health metrics in real-time"
    },
    {
      icon: Shield,
      title: "Secure & Private", 
      description: "Your health data is encrypted and protected with medical-grade security"
    },
    {
      icon: TrendingUp,
      title: "Smart Analytics",
      description: "AI-powered insights and recommendations for better health outcomes"
    },
    {
      icon: Users,
      title: "Care Team Access",
      description: "Share data seamlessly with your healthcare providers"
    }
  ];

  return (
    <div className="relative overflow-hidden">
      {/* Hero Section */}
      <section className="relative py-20 lg:py-32 bg-gradient-hero">
        <div className="container px-4 mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Content */}
            <div className="space-y-8 animate-fade-in">
              <div className="space-y-4">
                <h1 className="text-4xl lg:text-6xl font-bold text-foreground leading-tight">
                  Your Health,
                  <span className="text-primary"> Simplified</span>
                </h1>
                <p className="text-xl text-muted-foreground max-w-lg">
                  Upload your health data, get instant insights, and receive personalized recommendations from our AI-powered healthcare platform.
                </p>
              </div>
              
              <div className="flex flex-col sm:flex-row gap-4">
                <Button 
                  size="lg" 
                  className="bg-gradient-medical shadow-medical hover:scale-105 transition-transform"
                  onClick={() => navigate("/signup")}
                >
                  Get Started Free
                </Button>
                <Button 
                  size="lg" 
                  variant="outline"
                  onClick={() => navigate("/login")}
                >
                  Sign In
                </Button>
              </div>

              <div className="flex items-center space-x-6 text-sm text-muted-foreground">
                <div className="flex items-center">
                  <Shield className="h-4 w-4 text-primary mr-2" />
                  HIPAA Compliant
                </div>
                <div className="flex items-center">
                  <Heart className="h-4 w-4 text-primary mr-2" />
                  Trusted by 10K+ users
                </div>
              </div>
            </div>

            {/* Right Content - Health Dashboard Preview */}
            <div className="relative">
              <Card className="p-6 shadow-card-hover bg-card/50 backdrop-blur border animate-fade-in">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold text-lg">Health Overview</h3>
                    <div className="h-2 w-2 bg-health-normal rounded-full animate-pulse-medical"></div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <p className="text-sm text-muted-foreground">Blood Pressure</p>
                      <p className="text-2xl font-bold text-health-normal">120/80</p>
                      <p className="text-xs text-success">Normal</p>
                    </div>
                    <div className="space-y-2">
                      <p className="text-sm text-muted-foreground">Heart Rate</p>
                      <p className="text-2xl font-bold text-primary">72 BPM</p>
                      <p className="text-xs text-success">Excellent</p>
                    </div>
                    <div className="space-y-2">
                      <p className="text-sm text-muted-foreground">CBC Status</p>
                      <p className="text-2xl font-bold text-health-warning">Review</p>
                      <p className="text-xs text-warning">See Doctor</p>
                    </div>
                    <div className="space-y-2">
                      <p className="text-sm text-muted-foreground">BMI</p>
                      <p className="text-2xl font-bold text-health-normal">22.5</p>
                      <p className="text-xs text-success">Healthy</p>
                    </div>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-background">
        <div className="container px-4 mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold mb-4">
              Everything you need for
              <span className="text-primary"> better health</span>
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Our platform provides comprehensive health monitoring and insights to help you make informed decisions about your wellbeing.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <Card 
                key={index} 
                className="p-6 text-center hover:shadow-card-hover transition-all duration-300 hover:scale-105 animate-fade-in border-0 shadow-medical/20"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="mx-auto w-12 h-12 bg-gradient-medical rounded-full flex items-center justify-center mb-4">
                  <feature.icon className="h-6 w-6 text-white" />
                </div>
                <h3 className="font-semibold text-lg mb-2">{feature.title}</h3>
                <p className="text-muted-foreground text-sm">{feature.description}</p>
              </Card>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};