import os
import tempfile
import unittest
from unittest import mock

from backend.app.automation import run_daily_search
from backend.app.agents.job_hunter import _normalize_job_entry, fetch_live_jobs, fetch_live_jobs_with_target


class DailySearchFlowTests(unittest.TestCase):
    def test_remotive_uses_current_public_endpoint_and_real_url(self):
        class FakeResponse:
            status_code = 200
            def json(self):
                return {"jobs": [{
                    "title": "Director, Cloud Infrastructure",
                    "company_name": "Example Corp",
                    "url": "https://remotive.com/remote-jobs/software-dev/director-cloud-infrastructure-123456",
                    "candidate_required_location": "United States",
                    "description": "Lead AWS cloud infrastructure and platform engineering.",
                }]}

        with mock.patch("backend.app.agents.job_hunter.requests.get", return_value=FakeResponse()) as request:
            jobs = fetch_live_jobs(["Director Cloud Infrastructure"], "Remote")

        self.assertTrue(jobs)
        self.assertEqual(jobs[0]["source"], "Remotive")
        self.assertTrue(jobs[0]["apply_url"].startswith("https://remotive.com/"))
        self.assertTrue(any("https://remotive.com/api/remote-jobs" in call.args[0] for call in request.call_args_list))


    def test_run_daily_search_returns_summary_and_creates_assets(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["EXECUTIVE_DASHBOARD_DB_PATH"] = os.path.join(tmpdir, "application_state.db")
            sample_jobs = [{
                "id": f"test-job-{i}", "company": f"Company {i}", "title": "Director Cloud Infrastructure",
                "description": "Lead AWS, Terraform, platform engineering, and cloud modernization.",
                "url": f"https://careers.example.com/jobs/test-job-{i}", "apply_url": f"https://careers.example.com/jobs/test-job-{i}",
                "location": "Remote", "source": "Test",
            } for i in range(12)]
            with mock.patch("backend.app.automation.fetch_live_jobs_with_target", return_value=sample_jobs):
                summary = run_daily_search(output_dir=tmpdir, target_keywords=["Director Cloud Infrastructure", "VP Infrastructure"], target_location="Remote", min_new_jobs=10)
            self.assertIn("jobs_found", summary)
            self.assertGreaterEqual(summary["jobs_found"], 10)
            self.assertGreaterEqual(summary["documents_created"], 2)
            self.assertTrue(os.path.isdir(tmpdir))

    def test_fetch_live_jobs_with_target_filters_processed_and_reaches_target(self):
        mock_jobs = [{
            "id": f"job-{i}",
            "company": f"Corp {i}",
            "title": "VP of Platform Engineering",
            "url": f"https://example.com/job-{i}",
            "apply_url": f"https://example.com/job-{i}",
            "location": "Remote",
            "source": "MockSource"
        } for i in range(15)]

        processed_ids = {f"job-{i}" for i in range(3)}  # 3 jobs already processed

        with mock.patch("backend.app.agents.job_hunter.fetch_live_jobs", return_value=mock_jobs):
            new_jobs = fetch_live_jobs_with_target(["VP Platform Engineering"], "Remote", processed_job_ids=processed_ids, min_target=10)

        self.assertGreaterEqual(len(new_jobs), 10)
        for job in new_jobs:
            self.assertNotIn(job["id"], processed_ids)

    def test_normalize_job_entry_prefers_apply_url_and_company_name(self):
        candidate = {
            "url": "https://www.linkedin.com/jobs/view/3456789012/",
            "company": "",
            "company_name": "Northwind Systems",
            "title": "VP of Platform Engineering",
            "location": "Remote",
            "description": "Lead cloud and platform modernization",
            "source": "LinkedIn",
            "apply_url": "https://www.linkedin.com/jobs/view/3456789012/apply/"
        }

        normalized = _normalize_job_entry(candidate, "Remote")

        self.assertEqual(normalized["company"], "Northwind Systems")
        self.assertEqual(normalized["url"], "https://www.linkedin.com/jobs/view/3456789012/apply/")
        self.assertEqual(normalized["title"], "VP of Platform Engineering")

    def test_fetch_live_jobs_uses_listing_data_when_detail_page_fails(self):
        class FakeResponse:
            def __init__(self, status_code, text):
                self.status_code = status_code
                self.text = text

        search_html = '''
        <html><body>
          <div class="job-search-card">
            <a class="base-card__full-link" href="https://www.linkedin.com/jobs/view/1234567890">
              <h3>Senior Director, Platform Engineering</h3>
              <h4>Northwind Systems</h4>
              <span class="job-search-card__location">Remote</span>
            </a>
          </div>
        </body></html>
        '''

        def fake_get(url, headers=None, timeout=None, **kwargs):
            if 'jobs/search' in url:
                return FakeResponse(200, search_html)
            return FakeResponse(404, 'not found')

        with mock.patch('backend.app.agents.job_hunter.requests.get', side_effect=fake_get):
            jobs = fetch_live_jobs(['Senior Director Platform Engineering'], 'Remote')

        self.assertTrue(jobs)
        self.assertEqual(jobs[0]['title'], 'Senior Director, Platform Engineering')
        self.assertEqual(jobs[0]['company'], 'Northwind Systems')


if __name__ == "__main__":
    unittest.main()

