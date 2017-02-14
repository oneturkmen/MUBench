<?php

require_once('DatabaseTestCase.php');

class DatabaseTestCaseTest extends DatabaseTestCase
{

    function testTablesExist()
    {
        $tables = $this->db->queryToArray($this->pdo->query("SELECT name FROM sqlite_master WHERE type='table'"));

        $expectedTables = [
            ['name' => 'detectors'],
            ['name' => 'stats'],
            ['name' => 'metadata'],
            ['name' => 'patterns'],
            ['name' => 'reviews'],
            ['name' => 'meta_snippets'],
            ['name' => 'review_findings'],
            ['name' => 'review_findings_type'],
            ['name' => 'finding_snippets'],
            ['name' => 'types']
        ];

        self::assertEquals($expectedTables, $tables);
    }

    function testTypesInserted()
    {
        $types = $this->db->queryToArray($this->pdo->query("SELECT name FROM types"));

        $expectedTypes = [
            ['name' => 'missing/call'],
            ['name' => 'misplaced/call'],
            ['name' => 'superfluous/call'],
            ['name' => 'missing/condition/null_check'],
            ['name' => 'missing/condition/value_or_state'],
            ['name' => 'missing/condition/synchronization'],
            ['name' => 'missing/condition/context'],
            ['name' => 'misplaced/condition/null_check'],
            ['name' => 'misplaced/condition/value_or_state'],
            ['name' => 'misplaced/condition/synchronization'],
            ['name' => 'misplaced/condition/context'],
            ['name' => 'superfluous/condition/null_check'],
            ['name' => 'superfluous/condition/value_or_state'],
            ['name' => 'superfluous/condition/synchronization'],
            ['name' => 'superfluous/condition/context'],
            ['name' => 'missing/exception_handling'],
            ['name' => 'misplaced/exception_handling'],
            ['name' => 'superfluous/exception_handling'],
            ['name' => 'missing/iteration'],
            ['name' => 'misplaced/iteration'],
            ['name' => 'superfluous/iteration']
        ];

        self::assertEquals($expectedTypes, $types);
    }

}