import { useState } from 'react'
import { PlanForm } from '@/components/PlanForm'
import { PlanDisplay } from '@/components/PlanDisplay'
import '@/index.css'

function App() {
  const [plan, setPlan] = useState<any>(null)

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-4">
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="text-center space-y-2 mb-8">
          <h1 className="text-4xl md:text-5xl font-bold text-white">📚 Planora</h1>
          <p className="text-lg text-purple-200">AI-Powered Study Plan Generator</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <PlanForm onPlanGenerated={setPlan} />
          </div>
          <div className="lg:col-span-2">
            {plan ? (
              <PlanDisplay plan={plan} />
            ) : (
              <div className="text-center p-12 text-purple-200 bg-white/10 rounded-lg backdrop-blur">
                <p className="text-lg">Generate a study plan to get started</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
