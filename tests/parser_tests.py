from VMK_bot.pdf_parser import Parser
import unittest


class TestParser(unittest.TestCase):
    def test_day_converter(self):
        for i, day in enumerate(("Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье")):
            self.assertEqual(Parser.number_to_weekday(i), day)

    def test_import_to_db_1(self):
        res = Parser.parse_schedule("tests/test_tables/example.pdf")
        self.assertEqual(set(res.keys()),
                         {'101', '102', '103', '104', '105', '106', '119', '107', '108', '109', '110', '111', '112',
                          '113', '114', '115',
                          '116', '117', '118', '120', '141', '142'})

    def test_import_to_db_2(self):
        res = Parser.parse_schedule("tests/test_tables/example2.pdf")
        self.assertEqual(set(res.keys()),
                         {'201', '202', '203', '204', '205', '206', '219', '207', '208', '209', '210', '211', '212',
                          '213', '214', '215', '216', '217', '218', '220', '241', '242'})

    def test_import_to_db_3(self):
        res = Parser.parse_schedule("tests/test_tables/example3.pdf")
        self.assertEqual(set(res.keys()),
                         {'301', '302', '303', '304', '305', '306', '307', '309', '311', '312', '313', '314', '315',
                          '316', '317', '318', '319/1', '319/2', '320', '321', '323', '324', '325', '327', '328',
                          '341/1', '341/2'})

    def test_import_to_db_4(self):
        res = Parser.parse_schedule("tests/test_tables/example4.pdf")
        self.assertEqual(set(res.keys()),
                         {'401', '402', '403', '404', '405', '406', '407', '409', '411', '412', '413', '414', '415',
                          '416', '417', '418', '419/1', '419/2', '420', '421', '423', '424', '425', '427', '428',
                          '441/1', '441/2'})
