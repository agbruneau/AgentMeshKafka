package tui

import (
	"fmt"
	"strings"
	"time"

	"github.com/charmbracelet/bubbles/key"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

// updateAlgorithms handles key messages for the algorithms section.
func (m DashboardModel) updateAlgorithms(msg tea.KeyMsg) (tea.Model, tea.Cmd) {
	switch {
	case key.Matches(msg, m.keys.Up):
		if m.algorithms.cursor > 0 {
			m.algorithms.cursor--
		}
	case key.Matches(msg, m.keys.Down):
		if m.algorithms.cursor < len(m.algorithms.names)-1 {
			m.algorithms.cursor++
		}
	case key.Matches(msg, m.keys.Enter):
		// Start calculation with selected algorithm
		return m.startSingleCalculation()
	}
	return m, nil
}

// renderAlgorithmTable renders the algorithm comparison table.
func (m DashboardModel) renderAlgorithmTable() string {
	var b strings.Builder

	// Section title
	titleStyle := m.styles.BoxTitle
	if m.focusedSection == SectionAlgorithms {
		titleStyle = titleStyle.Foreground(m.styles.Primary.GetForeground())
	}
	b.WriteString(titleStyle.Render("ALGORITHMS"))
	b.WriteString("\n\n")

	// Table header - using same column widths as rows
	colRank := lipgloss.NewStyle().Width(3)
	colName := lipgloss.NewStyle().Width(25)
	colProgress := lipgloss.NewStyle().Width(30)
	colPct := lipgloss.NewStyle().Width(8).Align(lipgloss.Right)
	colDur := lipgloss.NewStyle().Width(12).Align(lipgloss.Right)
	colStatus := lipgloss.NewStyle().Width(6).Align(lipgloss.Center)

	header := lipgloss.JoinHorizontal(lipgloss.Center,
		"  ",
		colRank.Render("#"),
		" ",
		colName.Render("Algorithm"),
		" ",
		colProgress.Render("Progress"),
		" ",
		colPct.Render("%"),
		" ",
		colDur.Render("Duration"),
		" ",
		colStatus.Render("Status"),
	)
	b.WriteString(m.styles.TableHeader.Render(header))
	b.WriteString("\n")

	// Separator - adapt to terminal width (accounting for box padding)
	separatorWidth := m.width - 8
	if separatorWidth < 50 {
		separatorWidth = 50
	}
	if separatorWidth > 120 {
		separatorWidth = 120
	}
	b.WriteString(m.styles.Primary.Render(strings.Repeat("━", separatorWidth)))
	b.WriteString("\n")

	// Algorithm rows
	for i, name := range m.algorithms.names {
		row := m.renderAlgorithmRow(i, name)
		b.WriteString(row)
		b.WriteString("\n")
	}

	return b.String()
}

// renderAlgorithmRow renders a single algorithm row.
func (m DashboardModel) renderAlgorithmRow(idx int, name string) string {
	progress := m.algorithms.progresses[idx]
	duration := m.algorithms.durations[idx]
	status := m.algorithms.statuses[idx]

	// Row style with alternating backgrounds
	rowStyle := m.styles.TableRow
	if idx%2 == 1 {
		rowStyle = m.styles.TableRowAlt
	}
	if m.focusedSection == SectionAlgorithms && idx == m.algorithms.cursor {
		rowStyle = m.styles.MenuItemActive
	}

	// Column styles with fixed widths
	colRank := lipgloss.NewStyle().Width(3)
	colName := lipgloss.NewStyle().Width(25)
	colPct := lipgloss.NewStyle().Width(8).Align(lipgloss.Right)
	colDur := lipgloss.NewStyle().Width(12).Align(lipgloss.Right)
	colStatus := lipgloss.NewStyle().Width(6).Align(lipgloss.Center)

	// Rank column - keep as plain text, apply color separately
	rank := fmt.Sprintf("%d", idx+1)
	isWinner := false
	if status == StatusComplete && m.results.hasResults && len(m.results.results) > 0 {
		// Find position in results (sorted by duration)
		for pos, r := range m.results.results {
			if r.Name == name {
				rank = fmt.Sprintf("%d", pos+1)
				if pos == 0 {
					isWinner = true
				}
				break
			}
		}
	}

	// Truncate algorithm name to 25 characters max
	displayName := truncateString(name, 25)

	// Progress bar (always 30 chars wide)
	bar := m.renderProgressBar(progress, 30)

	// Percentage
	pct := fmt.Sprintf("%.1f%%", progress*100)

	// Duration column
	durStr := "-"
	if status == StatusComplete {
		durStr = formatDuration(duration)
	} else if status == StatusRunning && m.calculation.active {
		durStr = "..."
	}

	// Status indicator
	var statusStr string
	switch status {
	case StatusIdle:
		statusStr = m.styles.Muted.Render("IDLE")
	case StatusRunning:
		statusStr = m.styles.Info.Render("▶")
	case StatusComplete:
		statusStr = m.styles.Success.Render("OK")
	case StatusError:
		statusStr = m.styles.Error.Render("ERR")
	}

	// Render rank with color applied after width
	rankRendered := colRank.Render(rank)
	if isWinner {
		rankRendered = colRank.Foreground(m.styles.Success.GetForeground()).Render(rank)
	}

	// Build row using lipgloss for proper alignment with ANSI codes
	row := lipgloss.JoinHorizontal(lipgloss.Center,
		"  ",
		rankRendered,
		" ",
		colName.Render(displayName),
		" ",
		bar,
		" ",
		colPct.Render(pct),
		" ",
		colDur.Render(durStr),
		" ",
		colStatus.Render(statusStr),
	)

	return rowStyle.Render(row)
}

// truncateString truncates a string to maxLen characters, adding "..." if truncated.
func truncateString(s string, maxLen int) string {
	if len(s) <= maxLen {
		return s
	}
	if maxLen <= 3 {
		return s[:maxLen]
	}
	return s[:maxLen-3] + "..."
}

// renderProgressBar renders a progress bar.
func (m DashboardModel) renderProgressBar(progress float64, width int) string {
	filled := int(progress * float64(width))
	if filled > width {
		filled = width
	}

	filledStr := strings.Repeat("█", filled)
	emptyStr := strings.Repeat("░", width-filled)

	return m.styles.ProgressFilled.Render(filledStr) + m.styles.ProgressEmpty.Render(emptyStr)
}

// formatDuration formats a duration for display.
func formatDuration(d time.Duration) string {
	if d < time.Microsecond {
		return fmt.Sprintf("%dns", d.Nanoseconds())
	}
	if d < time.Millisecond {
		return fmt.Sprintf("%.1fµs", float64(d.Nanoseconds())/1000)
	}
	if d < time.Second {
		return fmt.Sprintf("%.1fms", float64(d.Microseconds())/1000)
	}
	if d < time.Minute {
		return fmt.Sprintf("%.2fs", d.Seconds())
	}
	return d.Round(time.Second).String()
}
