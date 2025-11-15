import { useState } from 'react'
import { savePlan, exportPdf } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { Download, Save } from 'lucide-react'

interface PlanDisplayProps {
  plan: any
  userId?: number
}

export function PlanDisplay({ plan, userId }: PlanDisplayProps) {
  const [saving, setSaving] = useState(false)
  const [exporting, setExporting] = useState(false)
  const [completed, setCompleted] = useState<Set<string>>(new Set())

  const handleSave = async () => {
    setSaving(true)
    try {
      await savePlan(plan, plan.course_type, plan.exam_date, userId)
      alert('Plan saved successfully!')
    } catch {
      alert('Failed to save plan')
    } finally {
      setSaving(false)
    }
  }

  const handleExport = async () => {
    setExporting(true)
    try {
      const response = await exportPdf(plan)
      const url = window.URL.createObjectURL(new Blob([response.data as BlobPart]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `planora_${plan.plan_length}days.pdf`)
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    } catch {
      alert('Failed to export PDF')
    } finally {
      setExporting(false)
    }
  }

  const toggleCompleted = (key: string) => {
    const newCompleted = new Set(completed)
    if (newCompleted.has(key)) {
      newCompleted.delete(key)
    } else {
      newCompleted.add(key)
    }
    setCompleted(newCompleted)
  }

  const formatTime = (minutes: number): string => {
    const h = Math.floor(minutes / 60)
    const m = minutes % 60
    if (h > 0) return `${h}h ${m}m`
    return `${m}m`
  }

  const reviewDays = plan.plan.filter((d: any) => d.is_review).length

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-5 gap-4">
        {[
          { label: 'Total Days', value: plan.plan_length },
          { label: 'Hours/Day', value: plan.hours_per_day },
          { label: 'Topics', value: plan.topics_count },
          { label: 'Review Days', value: reviewDays },
          { label: 'Review %', value: `${Math.round((plan.review_day_fraction || 0) * 100)}%` },
        ].map((metric) => (
          <Card key={metric.label} className="p-4">
            <div className="text-center">
              <p className="text-gray-600 text-sm">{metric.label}</p>
              <p className="text-2xl font-bold">{metric.value}</p>
            </div>
          </Card>
        ))}
      </div>

      <div className="space-y-4">
        {plan.plan.map((day: any) => (
          <Card
            key={day.day}
            className={`p-6 ${day.is_review ? 'border-yellow-300 bg-yellow-50' : 'bg-white'}`}
          >
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">
                  {day.is_review ? '🔄 Review Day' : '📖 Study Day'} — Day {day.day}
                </h3>
              </div>

              <p className="text-sm text-gray-700">⏱️ Study time: {plan.hours_per_day} hours</p>
              <p className="text-sm font-semibold">📝 {day.daily_summary}</p>

              <div className="space-y-3 mt-4">
                <p className="text-sm font-medium text-gray-700">Topics:</p>
                {day.topics?.map((topic: any, idx: number) => {
                  const key = `day_${day.day}_topic_${idx}`
                  const isChecked = completed.has(key)
                  return (
                    <div key={key} className="flex items-center gap-3 p-2 rounded hover:bg-gray-100">
                      <Checkbox
                        checked={isChecked}
                        onCheckedChange={() => toggleCompleted(key)}
                      />
                      <span className={`text-sm ${isChecked ? 'line-through text-gray-400' : ''}`}>
                        {idx + 1}. {topic.title} — {formatTime(topic.estimated_minutes)}
                      </span>
                    </div>
                  )
                })}
              </div>
            </div>
          </Card>
        ))}
      </div>

      <div className="flex gap-4">
        <Button onClick={handleSave} disabled={saving} className="flex-1 bg-green-600 hover:bg-green-700">
          <Save className="mr-2 h-4 w-4" /> Save Plan
        </Button>
        <Button onClick={handleExport} disabled={exporting} className="flex-1 bg-blue-600 hover:bg-blue-700">
          <Download className="mr-2 h-4 w-4" /> Export PDF
        </Button>
      </div>
    </div>
  )
}
