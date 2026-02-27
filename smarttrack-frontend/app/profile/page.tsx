import Sidebar from '../components/Sidebar';
import GlassmorphicLayout from '../components/GlassmorphicLayout';

export default function Profile() {
  const assessmentHistory = [
    { name: 'Mathematics Assessment', date: '2024-02-15', score: 88 },
    { name: 'Logical Reasoning Test', date: '2024-02-10', score: 92 },
    { name: 'Verbal Communication', date: '2024-02-05', score: 65 },
  ];

  return (
    <GlassmorphicLayout>
      <div className="flex min-h-screen">
        <Sidebar />
        
        <main className="flex-1">
          <header className="bg-white/5 backdrop-blur-2xl border-b border-white/10 px-8 py-6">
            <h1 className="text-2xl font-semibold text-white">Profile</h1>
          </header>

          <div className="p-8 max-w-4xl">
            <div className="bg-white/5 backdrop-blur-2xl rounded-2xl border border-white/10 p-8 mb-6">
              <div className="flex items-start gap-6 mb-8">
                <div className="w-24 h-24 bg-gradient-to-br from-lime-400 to-emerald-500 rounded-2xl flex items-center justify-center text-white text-3xl font-bold shadow-lg">
                  JD
                </div>
                <div className="flex-1">
                  <h2 className="text-2xl font-semibold text-white mb-2">Juan Dela Cruz</h2>
                  <p className="text-gray-400 mb-4">juan.delacruz@example.com</p>
                  <button className="px-4 py-2 border border-white/10 text-gray-300 rounded-xl hover:bg-white/5 transition">
                    Edit Profile
                  </button>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">Full Name</label>
                  <input
                    type="text"
                    value="Juan Dela Cruz"
                    readOnly
                    className="w-full px-4 py-2 border border-white/10 rounded-xl bg-white/5 text-white"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">Email</label>
                  <input
                    type="email"
                    value="juan.delacruz@example.com"
                    readOnly
                    className="w-full px-4 py-2 border border-white/10 rounded-xl bg-white/5 text-white"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">Grade Level</label>
                  <input
                    type="text"
                    value="Grade 12"
                    readOnly
                    className="w-full px-4 py-2 border-white/10 rounded-xl bg-white/5 text-white"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">School</label>
                  <input
                    type="text"
                    value="Sample High School"
                    readOnly
                    className="w-full px-4 py-2 border border-white/10 rounded-xl bg-white/5 text-white"
                  />
                </div>
              </div>
            </div>

            <div className="bg-white/5 backdrop-blur-2xl rounded-2xl border border-white/10 p-8">
              <h2 className="text-xl font-semibold text-white mb-6">Assessment History</h2>
              <div className="space-y-4">
                {assessmentHistory.map((assessment, index) => (
                  <div key={index} className="flex items-center justify-between p-4 border border-white/10 rounded-xl bg-white/5">
                    <div>
                      <h3 className="font-semibold text-white">{assessment.name}</h3>
                      <p className="text-sm text-gray-400">{assessment.date}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-semibold text-lime-400">{assessment.score}%</div>
                      <button className="text-sm text-lime-400 hover:text-lime-300">View Details</button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </main>
      </div>
    </GlassmorphicLayout>
  );
}
