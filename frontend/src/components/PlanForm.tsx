import { useState } from 'react'
import { generatePlan } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Card } from '@/components/ui/card'
import { Loader2 } from 'lucide-react'

interface PlanFormProps {
  onPlanGenerated: (plan: unknown) => void
}

export function PlanForm({ onPlanGenerated }: PlanFormProps) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [formData, setFormData] = useState({
    examType: 'final',
    hoursPerDay: 2,
    planLength: 14,
    courseType: 'General',
    reviewFraction: 8,
    syllabusText: '',
    manualTopics: '',
    examDate: new Date().toISOString().split('T')[0],
  })

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const fd = new FormData()
      fd.append('exam_type', formData.examType)
      fd.append('hours_per_day', formData.hoursPerDay.toString())
      fd.append('plan_length', formData.planLength.toString())
      fd.append('course_type', formData.courseType)
      fd.append('exam_date', formData.examDate)
      fd.append('review_day_fraction', (formData.reviewFraction / 100).toString())
      fd.append('syllabus_text', formData.syllabusText)
      fd.append('topics_text', formData.manualTopics)
      fd.append('use_ocr_gpu', 'false')

      const response = await generatePlan(fd)
      onPlanGenerated(response.data)
    } catch (err: unknown) {
      const error = err as any
      setError(error.response?.data?.error || 'Failed to generate plan')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="p-6 bg-gradient-to-br from-blue-50 to-indigo-50">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-2">
          <label className="block text-sm font-medium">Syllabus Text (optional)</label>
          <Textarea
            placeholder="Paste syllabus text here..."
            value={formData.syllabusText}
            onChange={(e) => setFormData({ ...formData, syllabusText: e.target.value })}
            className="h-24"
          />
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium">Manual Topics (one per line)</label>
          <Textarea
            placeholder="Enter topics manually..."
            value={formData.manualTopics}
            onChange={(e) => setFormData({ ...formData, manualTopics: e.target.value })}
            className="h-24"
          />
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="space-y-2">
            <label className="block text-sm font-medium">Exam Date</label>
            <Input
              type="date"
              value={formData.examDate}
              onChange={(e) => setFormData({ ...formData, examDate: e.target.value })}
            />
          </div>
          <div className="space-y-2">
            <label className="block text-sm font-medium">Hours/Day</label>
            <Input
              type="number"
              min="0.5"
              max="12"
              step="0.5"
              value={formData.hoursPerDay}
              onChange={(e) => setFormData({ ...formData, hoursPerDay: parseFloat(e.target.value) })}
            />
          </div>
          <div className="space-y-2">
            <label className="block text-sm font-medium">Days</label>
            <Input
              type="number"
              min="1"
              max="365"
              value={formData.planLength}
              onChange={(e) => setFormData({ ...formData, planLength: parseInt(e.target.value) })}
            />
          </div>
          <div className="space-y-2">
            <label className="block text-sm font-medium">Course</label>
            <Input
              value={formData.courseType}
              onChange={(e) => setFormData({ ...formData, courseType: e.target.value })}
              placeholder="e.g., Chemistry"
            />
          </div>
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium">Review Days: {formData.reviewFraction}%</label>
          <input
            type="range"
            min={0}
            max={30}
            value={formData.reviewFraction}
            onChange={(e) => setFormData({ ...formData, reviewFraction: parseInt(e.target.value) })}
            className="w-full"
          />
        </div>

        {error && <div className="text-red-600 text-sm">{error}</div>}

        <Button type="submit" disabled={loading} className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
          {loading ? <Loader2 className="animate-spin mr-2 h-4 w-4" /> : '🚀'} Generate Plan
        </Button>
      </form>
    </Card>
  )
}
