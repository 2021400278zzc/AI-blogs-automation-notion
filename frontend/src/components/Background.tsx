export function SpaceGrid() {
  return <div className="space-grid" aria-hidden="true" />
}

export function GradientOrbs() {
  return (
    <div aria-hidden="true">
      <div className="gradient-orb gradient-orb-brand animate-float" />
      <div className="gradient-orb gradient-orb-cyan animate-float" style={{ animationDelay: '-3s' }} />
    </div>
  )
}

export function GradientLines() {
  return (
    <div aria-hidden="true">
      <div className="gradient-line gradient-line-h" />
      <div className="gradient-line gradient-line-v hidden lg:block" />
      <div className="grid-scan-line" />
    </div>
  )
}
