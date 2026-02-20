'use client';

import Link from 'next/link';
import { motion, useScroll, useTransform } from 'framer-motion';
import { Brain, Target, BookOpen, CheckCircle2, Sparkles, TrendingUp, Award, Users, Zap } from 'lucide-react';

export default function Home() {
  const { scrollYProgress } = useScroll();
  const y = useTransform(scrollYProgress, [0, 1], ['0%', '50%']);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-emerald-900 to-lime-900 relative overflow-hidden">
      {/* Animated background blobs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            x: [0, 50, 0],
            y: [0, 30, 0],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className="absolute top-0 -left-40 w-96 h-96 bg-lime-500 rounded-full mix-blend-multiply filter blur-3xl opacity-30"
        />
        <motion.div
          animate={{
            scale: [1, 1.3, 1],
            x: [0, -30, 0],
            y: [0, 50, 0],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className="absolute top-0 -right-40 w-96 h-96 bg-emerald-500 rounded-full mix-blend-multiply filter blur-3xl opacity-30"
        />
        <motion.div
          animate={{
            scale: [1, 1.1, 1],
            x: [0, 40, 0],
            y: [0, -40, 0],
          }}
          transition={{
            duration: 12,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className="absolute -bottom-40 left-20 w-96 h-96 bg-lime-400 rounded-full mix-blend-multiply filter blur-3xl opacity-25"
        />
      </div>

      {/* Navbar */}
      <nav className="border-b border-white/10 relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ y: -100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.6 }}
            className="flex justify-between items-center h-14 sm:h-16"
          >
            <motion.div 
              className="flex items-center gap-2 sm:gap-3"
              whileHover={{ scale: 1.05 }}
            >
              <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-lime-400 to-emerald-500 rounded-lg sm:rounded-xl flex items-center justify-center shadow-lg shadow-lime-500/30">
                <Brain className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
              </div>
              <span className="text-lg sm:text-xl font-semibold text-white">SmartTrack</span>
            </motion.div>
            <Link 
              href="/login" 
              className="px-4 sm:px-5 py-1.5 sm:py-2 bg-white/10 backdrop-blur-sm text-white rounded-lg sm:rounded-xl hover:bg-white/20 transition border border-white/10 text-sm sm:text-base"
            >
              Login
            </Link>
          </motion.div>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-12 sm:pt-20 pb-16 sm:pb-24">
        <div className="text-center mb-12 sm:mb-16">
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ 
              type: "spring",
              stiffness: 260,
              damping: 20,
              delay: 0.2 
            }}
            className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-md rounded-full text-white mb-8 border border-white/20"
          >
            <Sparkles className="w-4 h-4 text-lime-400" />
            <span className="text-sm font-medium">AI-Powered Career Guidance</span>
          </motion.div>

          <motion.h1
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="text-4xl sm:text-5xl md:text-6xl font-bold text-white mb-4 sm:mb-6 px-4"
          >
            Find Your Perfect
            <br />
            <motion.span 
              className="text-lime-400"
              animate={{ 
                textShadow: [
                  "0 0 20px rgba(163, 230, 53, 0.5)",
                  "0 0 40px rgba(163, 230, 53, 0.8)",
                  "0 0 20px rgba(163, 230, 53, 0.5)",
                ]
              }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              University Program
            </motion.span>
          </motion.h1>

          <motion.p
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.5 }}
            className="text-base sm:text-xl text-gray-300 mb-8 sm:mb-10 max-w-3xl mx-auto px-4"
          >
            Intelligent assessment-based learning platform that analyzes your strengths 
            and recommends the best university programs for your future.
          </motion.p>

          <motion.div
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.7 }}
          >
            <Link 
              href="/register" 
              className="inline-block px-6 sm:px-8 py-3 sm:py-4 bg-lime-400 text-gray-900 font-semibold rounded-lg sm:rounded-xl hover:bg-lime-500 transition shadow-lg shadow-lime-500/30 hover:shadow-lime-500/50 hover:scale-105 transform text-sm sm:text-base"
            >
              Get Started Free
            </Link>
          </motion.div>
        </div>

        {/* Feature Cards with enhanced animations */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-6 mb-12 sm:mb-20">
          {[
            {
              icon: Brain,
              title: 'Smart Assessment',
              description: 'Take comprehensive academic and psychometric assessments tailored for SHS students',
              delay: 0.2,
              gradient: 'from-blue-500/20 to-cyan-500/20',
              iconColor: 'from-blue-400 to-cyan-500',
            },
            {
              icon: Target,
              title: 'Personalized Recommendations',
              description: 'Get AI-powered university program recommendations based on your unique strengths',
              delay: 0.4,
              gradient: 'from-purple-500/20 to-pink-500/20',
              iconColor: 'from-purple-400 to-pink-500',
            },
            {
              icon: BookOpen,
              title: 'Learning Center',
              description: 'Access curated learning modules to strengthen your skills and prepare for success',
              delay: 0.6,
              gradient: 'from-lime-500/20 to-emerald-500/20',
              iconColor: 'from-lime-400 to-emerald-500',
            },
          ].map((feature, index) => (
            <motion.div
              key={index}
              initial={{ y: 50, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.6, delay: feature.delay }}
              whileHover={{ 
                y: -10, 
                scale: 1.03,
                transition: { duration: 0.2 }
              }}
              className="group relative"
            >
              {/* Glow effect */}
              <motion.div 
                className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300`}
                animate={{
                  scale: [1, 1.1, 1],
                }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              />
              
              {/* Card */}
              <div className="relative bg-white/5 backdrop-blur-xl p-6 sm:p-8 rounded-xl sm:rounded-2xl border border-white/10 hover:border-white/20 transition-all h-full">
                <motion.div 
                  className={`w-12 h-12 sm:w-14 sm:h-14 bg-gradient-to-br ${feature.iconColor} rounded-lg sm:rounded-xl flex items-center justify-center mb-4 sm:mb-5 shadow-lg`}
                  whileHover={{ rotate: 360, scale: 1.1 }}
                  transition={{ duration: 0.6 }}
                >
                  <feature.icon className="w-6 h-6 sm:w-7 sm:h-7 text-white" />
                </motion.div>
                <h3 className="text-lg sm:text-xl font-semibold text-white mb-2 sm:mb-3">{feature.title}</h3>
                <p className="text-sm sm:text-base text-gray-400">{feature.description}</p>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Stats Section with animations */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="grid grid-cols-1 sm:grid-cols-3 gap-6 sm:gap-8 mb-12 sm:mb-20"
        >
          {[
            { value: '10K+', label: 'Students Helped', icon: Users },
            { value: '95%', label: 'Success Rate', icon: TrendingUp },
            { value: '500+', label: 'University Programs', icon: Award },
          ].map((stat, index) => (
            <motion.div
              key={index}
              initial={{ scale: 0 }}
              whileInView={{ scale: 1 }}
              viewport={{ once: true }}
              transition={{ 
                type: "spring",
                stiffness: 260,
                damping: 20,
                delay: index * 0.1 
              }}
              whileHover={{ scale: 1.05 }}
              className="relative group"
            >
              <div className="absolute inset-0 bg-lime-400/20 rounded-xl sm:rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div className="relative bg-white/5 backdrop-blur-xl rounded-xl sm:rounded-2xl p-6 sm:p-8 border border-white/10 hover:border-lime-400/50 transition-all text-center">
                <stat.icon className="w-10 h-10 sm:w-12 sm:h-12 text-lime-400 mx-auto mb-3 sm:mb-4" />
                <motion.div 
                  className="text-4xl sm:text-5xl font-bold text-lime-400 mb-2"
                  initial={{ opacity: 0 }}
                  whileInView={{ opacity: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: 0.3 + index * 0.1 }}
                >
                  {stat.value}
                </motion.div>
                <div className="text-sm sm:text-base text-gray-300 font-medium">{stat.label}</div>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* How It Works Section with stagger animation */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="relative group"
        >
          <div className="absolute inset-0 bg-gradient-to-br from-lime-500/10 to-emerald-500/10 rounded-xl sm:rounded-2xl blur-2xl"></div>
          <div className="relative bg-white/5 backdrop-blur-xl rounded-xl sm:rounded-2xl p-6 sm:p-12 border border-white/10 hover:border-white/20 transition-all">
            <motion.h2 
              initial={{ y: 20, opacity: 0 }}
              whileInView={{ y: 0, opacity: 1 }}
              viewport={{ once: true }}
              className="text-2xl sm:text-3xl font-bold text-white text-center mb-8 sm:mb-12"
            >
              How SmartTrack Works
            </motion.h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 sm:gap-8">
              {[
                { step: '1', title: 'Create Your Profile', description: 'Sign up and tell us about your academic background', icon: Users },
                { step: '2', title: 'Take Assessments', description: 'Complete academic and psychometric evaluations', icon: CheckCircle2 },
                { step: '3', title: 'Get Recommendations', description: 'Receive personalized university program matches', icon: Target },
                { step: '4', title: 'Learn & Improve', description: 'Access learning modules to strengthen your skills', icon: Zap },
              ].map((item, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 50 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: index * 0.15 }}
                  whileHover={{ y: -10, scale: 1.05 }}
                  className="text-center relative group/item"
                >
                  {/* Connecting line */}
                  {index < 3 && (
                    <motion.div 
                      initial={{ scaleX: 0 }}
                      whileInView={{ scaleX: 1 }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.5, delay: 0.5 + index * 0.15 }}
                      className="hidden lg:block absolute top-8 left-1/2 w-full h-0.5 bg-gradient-to-r from-lime-400/50 to-emerald-400/50 origin-left"
                    />
                  )}
                  
                  <motion.div 
                    className="relative w-14 h-14 sm:w-16 sm:h-16 bg-gradient-to-br from-lime-400 to-emerald-500 rounded-xl sm:rounded-2xl flex items-center justify-center text-2xl font-bold text-white mx-auto mb-3 sm:mb-4 shadow-lg shadow-lime-500/30"
                    whileHover={{ rotate: 360 }}
                    transition={{ duration: 0.6 }}
                  >
                    <item.icon className="w-7 h-7 sm:w-8 sm:h-8" />
                  </motion.div>
                  <h3 className="text-lg sm:text-xl font-semibold text-white mb-2">{item.title}</h3>
                  <p className="text-gray-400 text-sm">{item.description}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>

        {/* CTA Section */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="mt-12 sm:mt-20 text-center px-4"
        >
          <div className="relative group inline-block w-full max-w-4xl">
            <div className="absolute inset-0 bg-lime-400 rounded-xl sm:rounded-2xl blur-2xl opacity-50 group-hover:opacity-75 transition-opacity"></div>
            <div className="relative bg-gradient-to-r from-lime-400 to-emerald-500 rounded-xl sm:rounded-2xl p-8 sm:p-12 border border-lime-300">
              <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-3 sm:mb-4">Ready to Start Your Journey?</h2>
              <p className="text-sm sm:text-base text-gray-800 mb-4 sm:mb-6 max-w-2xl mx-auto">Join thousands of students who have found their perfect university program with SmartTrack</p>
              <Link 
                href="/register"
                className="inline-block px-6 sm:px-8 py-3 sm:py-4 bg-gray-900 text-white font-semibold rounded-lg sm:rounded-xl hover:bg-gray-800 transition shadow-lg hover:scale-105 transform text-sm sm:text-base"
              >
                Get Started Now
              </Link>
            </div>
          </div>
        </motion.div>
      </main>
    </div>
  );
}
