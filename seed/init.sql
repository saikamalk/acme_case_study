DROP TABLE IF EXISTS next_actions CASCADE;
DROP TABLE IF EXISTS issue_updates CASCADE;
DROP TABLE IF EXISTS issues CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
CREATE TABLE customers
(
    id             SERIAL PRIMARY KEY,
    name           VARCHAR(255) NOT NULL,
    industry       VARCHAR(255),
    account_status VARCHAR(50)
);
CREATE TABLE issues
(
    id          SERIAL PRIMARY KEY,
    customer_id INT  NOT NULL,
    title       TEXT NOT NULL,
    status      VARCHAR(50),
    priority    VARCHAR(50),
    CONSTRAINT fk_customer
        FOREIGN KEY (customer_id)
            REFERENCES customers (id)
            ON DELETE CASCADE
);
CREATE TABLE issue_updates
(
    id          SERIAL PRIMARY KEY,
    issue_id    INT  NOT NULL,
    update_text TEXT NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_issue_updates
        FOREIGN KEY (issue_id)
            REFERENCES issues (id)
            ON DELETE CASCADE
);
CREATE TABLE next_actions
(
    id          SERIAL PRIMARY KEY,
    issue_id    INT  NOT NULL,
    action_text TEXT NOT NULL,
    created_by  VARCHAR(255),
    created_at  TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    status      VARCHAR(50) DEFAULT 'Pending',
    CONSTRAINT fk_issue_actions
        FOREIGN KEY (issue_id)
            REFERENCES issues (id)
            ON DELETE CASCADE
);

INSERT INTO customers(name, industry, account_status)
VALUES
('Globex Corp', 'Retail', 'Active'),
('Initech', 'Healthcare', 'At Risk'),
('Umbrella Logistics', 'Logistics', 'Escalated'),
('Stark Industries', 'Manufacturing', 'Active'),
('Wayne Enterprises', 'Finance', 'VIP');

INSERT INTO issues(customer_id, title, status, priority)
VALUES
(1, 'Payment API timeout', 'Open', 'High'),
(1, 'Invoice mismatch', 'Open', 'Medium'),
(2, 'Delayed onboarding', 'Escalated', 'Critical'),
(3, 'Shipment tracking API failure', 'Open', 'Critical'),
(4, 'Reporting dashboard latency', 'Open', 'Low'),
(5, 'SSO login failure', 'Escalated', 'High');

INSERT INTO issue_updates(issue_id, update_text)
VALUES
(1, 'Engineering identified database connection leak'),
(1, 'Hotfix deployed to staging environment'),
(1, 'Customer reported intermittent improvement'),
(2, 'Finance team investigating invoice calculation discrepancy'),
(2, 'Awaiting updated tax configuration from client'),
(3, 'Customer escalated issue to account director'),
(3, 'Support team scheduled onboarding review call'),
(4, 'Shipment API failing for EU region'),
(4, 'Third-party logistics provider investigating issue'),
(5, 'Dashboard latency reproduced under high load testing'),
(5, 'Performance optimization patch under review'),
(6, 'Identity provider certificate expired'),
(6, 'Temporary authentication workaround deployed');

INSERT INTO next_actions(issue_id, action_text, created_by, status)
VALUES
(1, 'Monitor API latency after production deployment', 'admin1', 'Pending'),
(2, 'Schedule finance reconciliation meeting with customer', 'bob', 'Pending'),
(3, 'Arrange executive escalation call within 24 hours', 'admin1', 'In Progress'),
(4, 'Coordinate with logistics vendor for root cause analysis', 'bob', 'Pending'),
(5, 'Deploy dashboard caching optimization', 'admin1', 'Pending'),
(6, 'Renew SSO certificates and validate authentication flow', 'admin1', 'Completed');
