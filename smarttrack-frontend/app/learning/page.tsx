import Sidebar from '../components/Sidebar';
import GlassmorphicLayout from '../components/GlassmorphicLayout';

export default function Learning() {
  const modules = [
    {
      title: 'Mathematics Fundamentals',
      description: 'Strengthen your mathematical foundation',
      progress: 75,
      lessons: 12,
      completed: 9,
      category: 'Mathematics',
    },
    {
      title: 'Logical Reasoning',
      description: 'Enhance your analytical thinking skills',
      progress: 60,
      lessons: 10,
      completed: 6,
      category: 'Critical Thinking',
    },
    {
      title: 'Verbal Communication',
      description: 'Improve your communication abilities',
      progress: 40,
      lessons: 15,
      completed: 6,
      category: 'Communication',
    },
    {
      title: 'Problem Solving Techniques',
      description: 'Master various problem-solving strategies',
      progress: 90,
      lessons: 8,
      completed: 7,
      category: 'Problem Solving',
    },
    {
      title: 'Creative Writing',
      description: 'Develop your creative expression',
      progress: 25,
      lessons: 12,
      completed: 3,
      category: 'Writing',
    },
    {
      title: 'Data Analysis Basics',
      description: 'Introduction to data interpretation',
      progress: 0,
      lessons: 10,
      completed: 0,
      category: 'Data Science',
    },
  ];

  return (
    <GlassmorphicLayout>
      <div className="flex min-h-screen">
        <Sidebar />
        
        <main className="flex-1">
          <header className="bg-white/5 backdrop-blur-2xl border-b border-white/10 px-8 py-6">
            <h1 className="text-2xl font-semibold text-white">Learning Center</h1>
            <p className="text-gray-400 mt-1">Continue your learning journey</p>
          </header>

          <div className="p-8">
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {modules.map((module) => (
                <div key={module.title} className="bg-white/5 backdrop-blur-2xl rounded-2xl border border-white/10 p-6 hover:border-white/20 transition-all">
                  <div className="mb-4">
                    <span className="inline-block px-3 py-1 bg-lime-400/20 text-lime-400 text-xs font-semibold rounded mb-3">
                      {module.category}
                    </span>
                    <h3 className="text-xl font-semibold text-white mb-2">{module.title}</h3>
                    <p className="text-gray-400 text-sm">{module.description}</p>
                  </div>

                  <div className="mb-4">
                    <div className="flex justify-between text-sm text-gray-400 mb-2">
                      <span>{module.completed} of {module.lessons} lessons</span>
                      <span>{module.progress}%</span>
                    </div>
                    <div className="w-full bg-white/10 rounded-full h-2">
                      <div
                        className="bg-lime-400 h-2 rounded-full"
                        style={{ width: `${module.progress}%` }}
                      />
                    </div>
                  </div>

                  <button className="w-full px-4 py-2 bg-lime-400 text-gray-900 rounded-xl hover:bg-lime-500 transition font-semibold">
                    {module.progress === 0 ? 'Start Learning' : 'Continue'}
                  </button>
                </div>
              ))}
            </div>
          </div>
        </main>
      </div>
    </GlassmorphicLayout>
  );
}
