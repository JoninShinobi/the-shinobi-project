'use client';

import React, { useState, useEffect } from 'react';
import { Menu, X, ArrowRight, Shield, Zap, Code, Database, Globe, TrendingUp } from 'lucide-react';
import Link from 'next/link';
import Image from 'next/image';

// --- Components ---

const Logo = ({ className = "h-10", width = 200, height = 40 }: { className?: string; width?: number; height?: number }) => (
  <Image
    src="/logos/logo-light-accent.png"
    alt="The Shinobi Project"
    width={width}
    height={height}
    className={className}
    priority
  />
);

const SectionHeading = ({ title, subtitle }: { title: string; subtitle: string }) => (
  <div className="mb-12 md:mb-20">
    <h2 className="text-3xl md:text-5xl font-bold text-white mb-4 tracking-tight">{title}</h2>
    <div className="h-1 w-20 bg-red-700 mb-6"></div>
    <p className="text-zinc-400 text-lg md:text-xl max-w-2xl leading-relaxed">{subtitle}</p>
  </div>
);

const ServiceCard = ({ icon: Icon, title, description, benefits }: {
  icon: React.ElementType;
  title: string;
  description: string;
  benefits: string[]
}) => (
  <div className="group relative bg-zinc-900 border border-zinc-800 p-8 hover:border-red-900/50 transition-all duration-300 hover:shadow-2xl hover:shadow-red-900/10">
    <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
      <Icon size={64} className="text-zinc-500" />
    </div>
    <div className="mb-6 inline-block p-3 bg-zinc-950 border border-zinc-800 rounded-sm">
      <Icon className="text-red-600" size={28} />
    </div>
    <h3 className="text-2xl font-bold text-white mb-4 group-hover:text-red-500 transition-colors">{title}</h3>
    <p className="text-zinc-400 mb-6 leading-relaxed">{description}</p>
    <ul className="space-y-2">
      {benefits.map((benefit, index) => (
        <li key={index} className="flex items-start text-sm text-zinc-500 group-hover:text-zinc-300 transition-colors">
          <span className="mr-2 text-red-700">/</span> {benefit}
        </li>
      ))}
    </ul>
  </div>
);

const Button = ({ children, primary = false, className = "" }: {
  children: React.ReactNode;
  primary?: boolean;
  className?: string
}) => {
  const baseClass = "px-8 py-4 font-bold tracking-wide transition-all duration-300 flex items-center justify-center text-sm uppercase";
  const primaryClass = "bg-red-700 text-white hover:bg-red-800 shadow-lg shadow-red-900/20";
  const secondaryClass = "border border-zinc-700 text-zinc-300 hover:border-zinc-500 hover:text-white bg-transparent";

  return (
    <button className={`${baseClass} ${primary ? primaryClass : secondaryClass} ${className}`}>
      {children}
    </button>
  );
};

export default function ShinobiProject() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-300 font-sans selection:bg-red-900 selection:text-white">

      {/* Navigation */}
      <nav className={`fixed w-full z-50 transition-all duration-500 ${isScrolled ? 'bg-zinc-950/90 backdrop-blur-md border-b border-zinc-800 py-4' : 'bg-transparent py-6'}`}>
        <div className="container mx-auto px-6 flex justify-between items-center">
          <Link href="/" className="flex items-center">
            <Logo className="h-10 w-auto" width={200} height={40} />
          </Link>

          <div className="hidden md:flex items-center gap-8">
            <a href="#mission" className="text-xs font-medium hover:text-red-500 transition-colors uppercase tracking-widest">Directive</a>
            <a href="#services" className="text-xs font-medium hover:text-red-500 transition-colors uppercase tracking-widest">Arsenal</a>
            <a href="#philosophy" className="text-xs font-medium hover:text-red-500 transition-colors uppercase tracking-widest">Protocol</a>
            <Link href="/portfolio" className="text-xs font-medium hover:text-red-500 transition-colors uppercase tracking-widest">Deployments</Link>
            <button className="px-5 py-2 border border-red-700 text-red-500 hover:bg-red-700 hover:text-white transition-all duration-300 text-xs font-bold uppercase tracking-widest">
              Initiate
            </button>
          </div>

          <button className="md:hidden text-white" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? <X /> : <Menu />}
          </button>
        </div>
      </nav>

      {/* Mobile Menu Overlay */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-40 bg-zinc-950 flex flex-col items-center justify-center space-y-8">
          <a href="#mission" className="text-2xl font-bold text-white uppercase tracking-widest" onClick={() => setMobileMenuOpen(false)}>Directive</a>
          <a href="#services" className="text-2xl font-bold text-white uppercase tracking-widest" onClick={() => setMobileMenuOpen(false)}>Arsenal</a>
          <a href="#philosophy" className="text-2xl font-bold text-white uppercase tracking-widest" onClick={() => setMobileMenuOpen(false)}>Protocol</a>
          <Link href="/portfolio" className="text-2xl font-bold text-white uppercase tracking-widest" onClick={() => setMobileMenuOpen(false)}>Deployments</Link>
          <button className="px-8 py-3 bg-red-700 text-white font-bold uppercase" onClick={() => setMobileMenuOpen(false)}>Initiate Protocol</button>
        </div>
      )}

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 md:pt-48 md:pb-32 px-6 border-b border-zinc-900 overflow-hidden">
        {/* Abstract Background Element */}
        <div className="absolute top-0 right-0 w-1/2 h-full bg-gradient-to-l from-zinc-900/50 to-transparent skew-x-12 transform origin-top pointer-events-none" />

        <div className="container mx-auto relative z-10">
          <div className="max-w-4xl">
            <div className="inline-flex items-center gap-2 mb-6 px-3 py-1 bg-zinc-900 border border-zinc-800 rounded-full">
              <span className="w-2 h-2 rounded-full bg-red-600 animate-pulse"></span>
              <span className="text-xs uppercase tracking-widest font-semibold text-zinc-400">Silent Partners for Local Growth</span>
            </div>
            <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold text-white mb-8 leading-tight tracking-tight">
              Defend Your <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-600 to-red-800">Territory.</span>
            </h1>
            <p className="text-xl md:text-2xl text-zinc-400 mb-10 max-w-2xl leading-relaxed">
              We build the digital infrastructure small businesses need to outmaneuver corporate giants. You provide the craft; we provide the blade.
            </p>
            <div className="flex flex-col md:flex-row gap-4">
              <Button primary>Build My Infrastructure <ArrowRight className="ml-2 w-4 h-4" /></Button>
              <Link href="/portfolio">
                <Button>View Deployments</Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* The Enemy / Problem Section */}
      <section id="mission" className="py-24 px-6 bg-zinc-950">
        <div className="container mx-auto">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">The Landscape has Shifted.</h2>
              <p className="text-zinc-400 text-lg mb-6 leading-relaxed">
                Big retail chains and conglomerates don&apos;t win because they are better. They win because they have infrastructure you don&apos;t. They speak the confusing language of scale, logistics, and data.
              </p>
              <p className="text-zinc-400 text-lg mb-8 leading-relaxed">
                The Shinobi Project exists to level the playing field. We operate in the background, reinforcing your business with enterprise-grade tech and strategy, allowing you to remain independent and lethal.
              </p>
              <div className="flex items-center gap-4 text-white font-medium">
                <div className="h-px flex-1 bg-zinc-800"></div>
                <span>We handle the shadows. You handle the light.</span>
                <div className="h-px flex-1 bg-zinc-800"></div>
              </div>
            </div>
            <div className="relative">
              <div className="absolute inset-0 bg-red-900/20 blur-3xl rounded-full opacity-20"></div>
              <div className="relative grid grid-cols-2 gap-4">
                <div className="bg-zinc-900 p-6 border-l-2 border-red-700">
                  <h4 className="text-white font-bold mb-2">Automated Ops</h4>
                  <p className="text-sm text-zinc-500">Systems that run while you sleep.</p>
                </div>
                <div className="bg-zinc-900 p-6 border-l-2 border-zinc-700 translate-y-8">
                  <h4 className="text-white font-bold mb-2">Digital Fortification</h4>
                  <p className="text-sm text-zinc-500">Websites that convert and defend.</p>
                </div>
                <div className="bg-zinc-900 p-6 border-l-2 border-zinc-700">
                  <h4 className="text-white font-bold mb-2">Strategic Reach</h4>
                  <p className="text-sm text-zinc-500">Marketing that strikes precisely.</p>
                </div>
                <div className="bg-zinc-900 p-6 border-l-2 border-red-700 translate-y-8">
                  <h4 className="text-white font-bold mb-2">Local Dominance</h4>
                  <p className="text-sm text-zinc-500">Reclaim your community market.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section id="services" className="py-24 px-6 bg-black relative">
        <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-zinc-800 to-transparent"></div>
        <div className="container mx-auto">
          <SectionHeading
            title="The Arsenal"
            subtitle="We don't just build websites. We construct comprehensive business ecosystems designed to scale without your constant intervention."
          />

          <div className="grid md:grid-cols-3 gap-8">
            <ServiceCard
              icon={Globe}
              title="Digital Presence"
              description="High-performance, dark-mode-first web platforms designed to capture leads and project authority. Not just a brochure, but a tool."
              benefits={["SEO Architecture", "Conversion Optimization", "Mobile-First Design"]}
            />
            <ServiceCard
              icon={Database}
              title="Infrastructure"
              description="We untangle the confusing knots of CRM, inventory management, and automated scheduling. You lift a finger; we build the machine."
              benefits={["Automated Workflows", "Customer Data Mgmt", "Inventory Syncing"]}
            />
            <ServiceCard
              icon={TrendingUp}
              title="Growth Strategy"
              description="Tactical analysis of local competitors. We identify weaknesses in the big retailers' local armor and exploit them for your gain."
              benefits={["Competitor Analysis", "Local SEO Domination", "Targeted Campaigns"]}
            />
          </div>
        </div>
      </section>

      {/* The Philosophy / Approach */}
      <section id="philosophy" className="py-24 px-6 bg-zinc-950 border-t border-zinc-900">
        <div className="container mx-auto">
          <div className="bg-zinc-900 overflow-hidden relative">
            <div className="absolute top-0 left-0 w-2 h-full bg-red-700"></div>
            <div className="grid md:grid-cols-2">
              <div className="p-12 md:p-16 flex flex-col justify-center">
                <h3 className="text-2xl font-bold text-white mb-6 uppercase tracking-wider">The Shinobi Protocol</h3>
                <ul className="space-y-6">
                  <li className="flex items-start">
                    <Shield className="text-red-600 mr-4 mt-1 shrink-0" size={24} />
                    <div>
                      <h4 className="text-white font-bold text-lg">Protection First</h4>
                      <p className="text-zinc-500 mt-1">We safeguard your time and your brand identity.</p>
                    </div>
                  </li>
                  <li className="flex items-start">
                    <Zap className="text-red-600 mr-4 mt-1 shrink-0" size={24} />
                    <div>
                      <h4 className="text-white font-bold text-lg">Precision Execution</h4>
                      <p className="text-zinc-500 mt-1">No bloat. No confusing jargon. Just systems that work.</p>
                    </div>
                  </li>
                  <li className="flex items-start">
                    <Code className="text-red-600 mr-4 mt-1 shrink-0" size={24} />
                    <div>
                      <h4 className="text-white font-bold text-lg">Invisible Tech</h4>
                      <p className="text-zinc-500 mt-1">Complex code hidden behind simple, elegant interfaces.</p>
                    </div>
                  </li>
                </ul>
              </div>
              <div className="bg-zinc-950/50 p-12 md:p-16 flex items-center justify-center border-l border-zinc-800">
                <div className="text-center">
                  <Logo className="mx-auto mb-6 opacity-80" width={300} height={60} />
                  <p className="text-xl text-white font-light italic">&quot;To act without being seen. To build without burden.&quot;</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-black py-12 px-6 border-t border-zinc-900">
        <div className="container mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-8 mb-12">
            <Link href="/" className="flex items-center">
              <Logo className="h-8 w-auto" width={160} height={32} />
            </Link>
            <div className="flex gap-8 text-xs text-zinc-500 uppercase tracking-widest">
              <a href="#services" className="hover:text-white transition-colors">Arsenal</a>
              <a href="#philosophy" className="hover:text-white transition-colors">Protocol</a>
              <Link href="/portfolio" className="hover:text-white transition-colors">Deployments</Link>
            </div>
          </div>
          <div className="flex flex-col md:flex-row justify-between items-center text-xs text-zinc-600 uppercase tracking-widest border-t border-zinc-900 pt-8">
            <p>&copy; {new Date().getFullYear()} The Shinobi Project</p>
            <p>Forged in the Shadows</p>
          </div>
        </div>
      </footer>

    </div>
  );
}
