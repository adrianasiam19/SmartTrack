'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Programme, SHSLevel, getStoredUser, updateUserProfile, storeUser } from '../../lib/authApi';

interface ScreenCreateProfileProps {
  onNext: () => void;
}

const PROGRAMMES: Programme[] = ['General Science', 'General Arts', 'Business', 'Visual Arts', 'Home Economics', 'Technical'];
const SHS_LEVELS: SHSLevel[] = ['SHS 1', 'SHS 2', 'SHS 3', 'Completed SHS'];

export default function ScreenCreateProfile({ onNext }: ScreenCreateProfileProps) {
  const [fullName, setFullName] = useState('');
  const [school, setSchool] = useState('');
  const [shsLevel, setShsLevel] = useState<SHSLevel | ''>('');
  const [programme, setProgramme] = useState<Programme | ''>('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showContent, setShowContent] = useState(false);

  useEffect(() => {
    const stored = getStoredUser();
    if (stored) {
      setFullName(stored.full_name || '');
      setSchool(stored.school || '');
      if (stored.shs_level) setShsLevel(stored.shs_level as SHSLevel);
      if (stored.programme) setProgramme(stored.programme as Programme);
    }
    const t = setTimeout(() => setShowContent(true), 100);
    return () => clearTimeout(t);
  }, []);

  const formComplete = fullName.trim().length >= 2 && !!shsLevel && !!programme;

  const handleContinue = async () => {
    if (!formComplete) return;
    setIsSubmitting(true);
    try {
      await updateUserProfile({
        full_name: fullName.trim(),
        shs_level: shsLevel as SHSLevel,
        programme: programme as Programme,
        school: school.trim() || null,
      });
    } catch {
      // Silently continue - user data is saved locally
      const current = getStoredUser();
      if (current) {
        storeUser({ ...current, full_name: fullName.trim(), shs_level: shsLevel as SHSLevel, programme: programme as Programme, school: school.trim() || null });
      }
    }
    setTimeout(() => onNext(), 300);
  };

  const inputClasses = 'w-full px-4 py-3.5 bg-white border-2 border-[#E2E8F0] rounded-xl text-[#1E293B] placeholder-[#94A3B8] focus:ring-0 focus:border-[#2563EB] outline-none transition-all duration-200 text-base hover:border-[#C7D2FE]';
  const labelClasses = 'block text-sm font-semibold text-[#475569] mb-1.5';

  return (
    <AnimatePresence>
      {showContent && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.5 }}
          className="min-h-screen bg-[#F8FAFC] flex items-center justify-center relative overflow-hidden py-12 px-4 sm:px-6"
        >
          <div className="absolute inset-0 pointer-events-none">
            <div className="absolute top-0 -left-40 w-[400px] h-[400px] bg-[#2563EB]/4 rounded-full blur-3xl" />
            <div className="absolute bottom-0 -right-40 w-[400px] h-[400px] bg-[#7C3AED]/4 rounded-full blur-3xl" />
          </div>

          <div className="relative z-10 w-full max-w-lg mx-auto">
            {/* Header */}
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="text-center mb-10"
            >
              <div className="w-14 h-14 mx-auto bg-gradient-to-br from-[#2563EB] to-[#7C3AED] rounded-2xl flex items-center justify-center shadow-lg shadow-[#2563EB]/20 mb-4">
                <span className="text-white font-bold text-xl">A</span>
              </div>
              <h2 className="text-3xl sm:text-4xl font-bold text-[#1E293B] mb-2">
                Create Your Profile
              </h2>
              <p className="text-base text-[#475569] max-w-sm mx-auto">
                Help Atlas get to know you better for a personalized experience.
              </p>
            </motion.div>

            {/* Form */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="bg-white rounded-2xl border border-[#E2E8F0] p-8 shadow-xl shadow-[#2563EB]/5"
            >
              <div className="space-y-5">
                {/* Full Name */}
                <div>
                  <label className={labelClasses}>Full Name</label>
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className={inputClasses}
                    placeholder="e.g. Ama Owusu"
                    disabled={isSubmitting}
                  />
                </div>

                {/* School */}
                <div>
                  <label className={labelClasses}>
                    School{' '}
                    <span className="text-[#94A3B8] font-normal">(optional)</span>
                  </label>
                  <input
                    type="text"
                    value={school}
                    onChange={(e) => setSchool(e.target.value)}
                    className={inputClasses}
                    placeholder="e.g. Achimota School"
                    disabled={isSubmitting}
                  />
                </div>

                {/* SHS Level */}
                <div>
                  <label className={labelClasses}>SHS Level</label>
                  <select
                    value={shsLevel}
                    onChange={(e) => setShsLevel(e.target.value as SHSLevel | '')}
                    className="w-full px-4 py-3.5 bg-white border-2 border-[#E2E8F0] rounded-xl text-[#1E293B] focus:border-[#2563EB] outline-none transition-all duration-200 text-base appearance-none hover:border-[#C7D2FE] cursor-pointer bg-[url('data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20width%3D%2220%22%20height%3D%2220%22%20fill%3D%22none%22%20stroke%3D%22%2394A3B8%22%20stroke-width%3D%222%22%3E%3Cpath%20d%3D%22m6%208%204%204%204-4%22/%3E%3C/svg%3E')] bg-[length:20px] bg-[right_16px_center] bg-no-repeat"
                    disabled={isSubmitting}
                  >
                    <option value="" disabled>Choose your SHS level</option>
                    {SHS_LEVELS.map((level) => (
                      <option key={level} value={level}>{level}</option>
                    ))}
                  </select>
                </div>

                {/* Programme */}
                <div>
                  <label className={labelClasses}>Programme</label>
                  <div className="relative">
                    <select
                      value={programme}
                      onChange={(e) => setProgramme(e.target.value as Programme | '')}
                      className="w-full px-4 py-3.5 bg-white border-2 border-[#E2E8F0] rounded-xl text-[#1E293B] focus:border-[#2563EB] outline-none transition-all duration-200 text-base appearance-none hover:border-[#C7D2FE] cursor-pointer bg-[url('data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20width%3D%2220%22%20height%3D%2220%22%20fill%3D%22none%22%20stroke%3D%22%2394A3B8%22%20stroke-width%3D%222%22%3E%3Cpath%20d%3D%22m6%208%204%204%204-4%22/%3E%3C/svg%3E')] bg-[length:20px] bg-[right_16px_center] bg-no-repeat"
                      disabled={isSubmitting}
                    >
                      <option value="" disabled>Choose your programme</option>
                      {PROGRAMMES.map((p) => (
                        <option key={p} value={p}>{p}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* Continue button */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="mt-8"
              >
                <motion.button
                  whileHover={formComplete ? { scale: 1.02 } : {}}
                  whileTap={formComplete ? { scale: 0.98 } : {}}
                  onClick={handleContinue}
                  disabled={!formComplete || isSubmitting}
                  className={`w-full py-3.5 rounded-xl font-bold text-base transition-all duration-300 ${
                    formComplete && !isSubmitting
                      ? 'bg-gradient-to-r from-[#2563EB] to-[#7C3AED] text-white shadow-lg shadow-[#2563EB]/20 hover:shadow-xl'
                      : 'bg-[#E2E8F0] text-[#94A3B8] cursor-not-allowed'
                  }`}
                >
                  {isSubmitting ? 'Saving...' : formComplete ? 'Continue' : 'Complete your profile'}
                </motion.button>
              </motion.div>
            </motion.div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
