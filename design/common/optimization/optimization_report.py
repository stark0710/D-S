"""
Fixed-Wing/Multirotor/VTOL Shared Optimization Report

Compiles optimization outputs and rankings into structured Markdown reports.
"""

from backend.design.common.optimization.optimization_result import OptimizationResult

class OptimizationReport:
    """
    Formatter translating optimization result states into readable summaries.
    """
    @staticmethod
    def generate_markdown(result: OptimizationResult) -> str:
        md = []
        md.append("# Design Synthesis Optimization Report")
        md.append("---")
        md.append("## 1. Optimization Executive Summary")
        md.append(f"- **Success Status**: {'SUCCESS' if result.success else 'FAILED'}")
        md.append(f"- **Message**: {result.message}")
        md.append(f"- **Execution Time**: {result.execution_time_seconds:.4f} s")
        md.append(f"- **Iterations Completed**: {result.iteration_count}")
        md.append(f"- **Candidates Evaluated**: {result.evaluated_count}")
        md.append(f"- **Feasible Designs Found**: {result.feasible_count}")
        
        md.append("\n## 2. Winning Design Candidate")
        if result.success and result.winning_candidate:
            cand = result.winning_candidate
            md.append("| Design Variable | Value |")
            md.append("| :--- | :--- |")
            for k, v in cand.design_variables.items():
                md.append(f"| {k} | {v} |")
            
            md.append("\n### Derived Outputs")
            md.append("| Derived Variable | Value |")
            md.append("| :--- | :--- |")
            for k, v in cand.derived_variables.items():
                md.append(f"| {k} | {v} |")
                
            md.append(f"\n- **Winning Score**: {cand.overall_score:.4f}")
        else:
            md.append("*No valid winning candidate was selected.*")

        md.append("\n## 3. Constraint Analysis Summary")
        if result.history:
            total_rejected = result.evaluated_count - result.feasible_count
            md.append(f"- Total Rejected Candidates: {total_rejected}")
            fail_counts = {}
            for cand in result.history:
                if not cand.constraints_passed:
                    for name, res in cand.constraint_results.items():
                        if res["status"] == "FAIL":
                            fail_counts[name] = fail_counts.get(name, 0) + 1
            if fail_counts:
                md.append("\n| Constraint Rule | Rejection Count |")
                md.append("| :--- | :--- |")
                for name, count in fail_counts.items():
                    md.append(f"| {name} | {count} |")
            else:
                md.append("*No constraints failed.*")
        else:
            md.append("*No execution history available.*")

        md.append("\n## 4. Objective Score Rankings")
        if result.success and result.winning_candidate:
            md.append("| Objective Function | Raw Score |")
            md.append("| :--- | :--- |")
            for k, v in result.winning_candidate.objective_scores.items():
                md.append(f"| {k} | {v:.4f} |")

        return "\n".join(md)
