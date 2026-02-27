import Sidebar from '../components/Sidebar';
import GlassmorphicLayout from '../components/GlassmorphicLayout';

export default function Recommendations() {
  const programs = [
    {
      name: 'Computer Science',
      university: 'University of the Philippines',
      match: 95,
      strengths: ['Logical Reasoning', 'Mathematics', 'Problem Solving'],
      description: 'This program aligns perfectly with your analytical skills and mathematical aptitude.',
    },
    {
      name: 'Software Engineering',
      university: 'Ateneo de Manila University',
      match: 92,
      strengths: ['Problem Solving', 'Logical Reasoning'],
      description: 'Your strong problem-solving abilities make you an excellent fit for this program.',
    },
    {
      name: 'Data Science',
      university: 'De La Salle University',
      match: 88,
      strengths: ['Mathematics', 'Analytical Thinking'],
      description: 'Your mathematical foundation is ideal for pursuing data science.',
    },
    {
      name: 'Information Technology',
      university: 'University of Santo Tomas',
      match: 85,
      strengths: ['Technical Skills', 'Problem Solving'],
      description: 'A practical program that matches your technical aptitude.',
    },
  ];

  return (
    <GlassmorphicLayout>
      <div className="flex min-h-screen">
        <Sidebar />
        
        <main className="flex-1">
          <header className="bg-white/5 backdrop-blur-2xl border-b border-white/10 px-8 py-6">
            <h1 className="text-2xl font-semibold text-white">Program Recommendations</h1>
            <p className="text-gray-400 mt-1">Based on your assessment results and strengths</p>
          </header>

          <div className="p-8">
            <div className="grid gap-6">
              {programs.map((program) => (
                <div key={program.name} className="bg-white/5 backdrop-blur-2xl rounded-2xl border border-white/10 p-6 hover:border-white/20 transition-all">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h2 className="text-2xl font-semibold text-white">{program.name}</h2>
                        <span className="inline-block bg-lime-400 text-gray-900 text-sm font-semibold px-3 py-1 rounded-lg">
                          {program.match}% Match
                        </span>
                      </div>
                      <p className="text-gray-400">{program.university}</p>
                    </div>
                  </div>

                  <p className="text-gray-300 mb-4">{program.description}</p>

                  <div className="mb-4">
                    <h3 className="text-sm font-semibold text-gray-400 mb-2">Related Strengths:</h3>
                    <div className="flex flex-wrap gap-2">
                      {program.strengths.map((strength) => (
                        <span
                          key={strength}
                          className="px-3 py-1 bg-lime-400/20 text-lime-400 text-sm rounded-lg"
                        >
                          {strength}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="flex gap-3">
                    <button className="px-6 py-2 bg-lime-400 text-gray-900 rounded-xl hover:bg-lime-500 transition font-semibold">
                      View Details
                    </button>
                    <button className="px-6 py-2 border border-white/10 text-gray-300 rounded-xl hover:bg-white/5 transition">
                      Save for Later
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </main>
      </div>
    </GlassmorphicLayout>
  );
}
