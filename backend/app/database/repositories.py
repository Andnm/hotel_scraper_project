import json
from datetime import datetime, date
from typing import List, Dict, Optional
from app.core.database import get_db_connection

class CrawlHistoryRepository:
    
    def create_history(self, crawl_date: date, crawl_target: str, source: str = 'booking') -> int:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                query = """
                    INSERT INTO crawl_history (crawl_date, crawl_target, source, total_records)
                    VALUES (%s, %s, %s, 0)
                """
                cursor.execute(query, (crawl_date, crawl_target, source))
                conn.commit()
                history_id = cursor.lastrowid
                return history_id
            except Exception as e:
                conn.rollback()
                raise Exception(f"Error creating history: {str(e)}")
            finally:
                cursor.close()
    
    def get_all_histories(
        self, 
        limit: int = 50, 
        offset: int = 0, 
        source_filter: Optional[str] = None, 
        date_from: Optional[date] = None, 
        date_to: Optional[date] = None
    ) -> List[Dict]:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                query = "SELECT * FROM crawl_history WHERE 1=1"
                params = []
                
                if source_filter and source_filter.lower() != "tất cả":
                    query += " AND source = %s"
                    params.append(source_filter.lower())
                
                if date_from:
                    query += " AND crawl_date >= %s"
                    params.append(date_from)
                
                if date_to:
                    query += " AND crawl_date <= %s"
                    params.append(date_to)
                
                query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                results = cursor.fetchall()
                return results
            except Exception as e:
                raise Exception(f"Error getting histories: {str(e)}")
            finally:
                cursor.close()
    
    def get_history_by_id(self, history_id: int) -> Optional[Dict]:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                query = "SELECT * FROM crawl_history WHERE id = %s"
                cursor.execute(query, (history_id,))
                result = cursor.fetchone()
                return result
            except Exception as e:
                raise Exception(f"Error getting history: {str(e)}")
            finally:
                cursor.close()
    
    def update_total_records(self, history_id: int, total_records: int):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                query = "UPDATE crawl_history SET total_records = %s WHERE id = %s"
                cursor.execute(query, (total_records, history_id))
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise Exception(f"Error updating total records: {str(e)}")
            finally:
                cursor.close()
    
    def delete_history(self, history_id: int):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                query = "DELETE FROM crawl_history WHERE id = %s"
                cursor.execute(query, (history_id,))
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise Exception(f"Error deleting history: {str(e)}")
            finally:
                cursor.close()
    
    def get_total_count(
        self, 
        source_filter: Optional[str] = None, 
        date_from: Optional[date] = None, 
        date_to: Optional[date] = None
    ) -> int:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                query = "SELECT COUNT(*) FROM crawl_history WHERE 1=1"
                params = []
                
                if source_filter and source_filter.lower() != "tất cả":
                    query += " AND source = %s"
                    params.append(source_filter.lower())
                
                if date_from:
                    query += " AND crawl_date >= %s"
                    params.append(date_from)
                
                if date_to:
                    query += " AND crawl_date <= %s"
                    params.append(date_to)
                
                cursor.execute(query, params)
                count = cursor.fetchone()[0]
                return count
            except Exception as e:
                raise Exception(f"Error getting count: {str(e)}")
            finally:
                cursor.close()

    def get_latest_history(self, source: Optional[str] = None) -> Optional[Dict]:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                query = "SELECT * FROM crawl_history WHERE 1=1"
                params = []

                if source:
                    query += " AND source = %s"
                    params.append(source.lower())

                query += " ORDER BY created_at DESC LIMIT 1"

                cursor.execute(query, params)
                result = cursor.fetchone()
                return result
            except Exception as e:
                raise Exception(f"Error getting latest history: {str(e)}")
            finally:
                cursor.close()


class CrawlDataRepository:
    
    def save_batch_data(self, history_id: int, data_list: List[Dict]) -> int:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                values = []
                for data in data_list:
                    price_after = self._parse_numeric(data.get('Giá sau giảm', 'N/A'))
                    price_orig = self._parse_numeric(data.get('Giá gốc', 'N/A'))
                    review_count = self._parse_int(data.get('Số lượng review', 'N/A'))
                    review_score = self._parse_float(data.get('Điểm review', 'N/A'))
                    num_people = self._parse_int(data.get('Số lượng người', 'N/A'))
                    
                    options = {
                        'row_number': data.get('Hàng_gốc'),
                        'facilities': data.get('Các lựa chọn', 'N/A'),
                        'target_date': data.get('Ngày cần cào', '')
                    }
                    
                    values.append((
                        history_id,
                        data.get('Tên khách sạn', 'N/A'),
                        data.get('Link khách sạn', ''),
                        price_after,
                        price_orig,
                        review_count,
                        review_score,
                        data.get('Tên hạng phòng', 'N/A'),
                        num_people,
                        data.get('Giường', 'N/A'),
                        data.get('Diện tích phòng', 'N/A'),
                        json.dumps(options, ensure_ascii=False)
                    ))
                
                query = """
                    INSERT INTO crawl_data (
                        history_id, hotel_name, hotel_link, price_after_discount,
                        price_original, review_count, review_score, room_type,
                        num_people, bed_info, room_area, options
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.executemany(query, values)
                conn.commit()
                rows_inserted = cursor.rowcount
                return rows_inserted
            except Exception as e:
                conn.rollback()
                raise Exception(f"Error saving batch data: {str(e)}")
            finally:
                cursor.close()
    
    def get_data_by_history(self, history_id: int, limit: int = 100, offset: int = 0) -> List[Dict]:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                query = """
                    SELECT 
                        cd.*,
                        ch.crawl_date,
                        ch.crawl_target
                    FROM crawl_data cd
                    JOIN crawl_history ch ON cd.history_id = ch.id
                    WHERE cd.history_id = %s 
                    ORDER BY cd.id 
                    LIMIT %s OFFSET %s
                """
                cursor.execute(query, (history_id, limit, offset))
                results = cursor.fetchall()
                
                for row in results:
                    if row['options'] and isinstance(row['options'], str):
                        row['options'] = json.loads(row['options'])
                
                return results
            except Exception as e:
                raise Exception(f"Error getting data: {str(e)}")
            finally:
                cursor.close()
    
    def get_data_count(self, history_id: int) -> int:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                query = "SELECT COUNT(*) FROM crawl_data WHERE history_id = %s"
                cursor.execute(query, (history_id,))
                count = cursor.fetchone()[0]
                return count
            except Exception as e:
                raise Exception(f"Error getting data count: {str(e)}")
            finally:
                cursor.close()
    
    def export_data_by_history(self, history_id: int) -> List[Dict]:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                query = """
                    SELECT 
                        cd.*,
                        ch.crawl_date,
                        ch.crawl_target
                    FROM crawl_data cd
                    JOIN crawl_history ch ON cd.history_id = ch.id
                    WHERE cd.history_id = %s
                    ORDER BY cd.id
                """
                cursor.execute(query, (history_id,))
                results = cursor.fetchall()
                
                for row in results:
                    if row['options'] and isinstance(row['options'], str):
                        row['options'] = json.loads(row['options'])
                
                return results
            except Exception as e:
                raise Exception(f"Error exporting data: {str(e)}")
            finally:
                cursor.close()

    def export_all_data(self) -> List[Dict]:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                query = """
                    SELECT 
                        cd.*,
                        ch.crawl_date,
                        ch.crawl_target
                    FROM crawl_data cd
                    JOIN crawl_history ch ON cd.history_id = ch.id
                    ORDER BY ch.created_at, cd.id
                """
                cursor.execute(query)
                results = cursor.fetchall()
                
                for row in results:
                    if row['options'] and isinstance(row['options'], str):
                        row['options'] = json.loads(row['options'])
                
                return results
            except Exception as e:
                raise Exception(f"Error exporting all data: {str(e)}")
            finally:
                cursor.close()

    def export_data_by_filters(
        self,
        source_filter: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> List[Dict]:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                query = """
                    SELECT 
                        cd.*,
                        ch.crawl_date,
                        ch.crawl_target
                    FROM crawl_data cd
                    JOIN crawl_history ch ON cd.history_id = ch.id
                    WHERE 1=1
                """
                params = []

                if source_filter and source_filter.lower() != "tất cả":
                    query += " AND ch.source = %s"
                    params.append(source_filter.lower())

                if date_from:
                    query += " AND ch.crawl_date >= %s"
                    params.append(date_from)

                if date_to:
                    query += " AND ch.crawl_date <= %s"
                    params.append(date_to)

                query += " ORDER BY ch.crawl_date, cd.id"

                cursor.execute(query, params)
                results = cursor.fetchall()
                
                for row in results:
                    if row['options'] and isinstance(row['options'], str):
                        row['options'] = json.loads(row['options'])
                
                return results
            except Exception as e:
                raise Exception(f"Error exporting filtered data: {str(e)}")
            finally:
                cursor.close()
    
    @staticmethod
    def _parse_numeric(value):
        if value in ['N/A', '', None]:
            return None
        try:
            cleaned = ''.join(c for c in str(value) if c.isdigit() or c == '.')
            return float(cleaned) if cleaned else None
        except:
            return None
    
    @staticmethod
    def _parse_int(value):
        if value in ['N/A', '', None]:
            return None
        try:
            cleaned = ''.join(c for c in str(value) if c.isdigit())
            return int(cleaned) if cleaned else None
        except:
            return None
    
    @staticmethod
    def _parse_float(value):
        if value in ['N/A', '', None]:
            return None
        try:
            return float(value)
        except:
            return None
