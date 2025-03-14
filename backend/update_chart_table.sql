-- 修改charts表的user_id字段为可为空
ALTER TABLE charts MODIFY COLUMN user_id VARCHAR(36) NULL;

-- 删除外键约束（如果存在）
ALTER TABLE charts DROP FOREIGN KEY charts_ibfk_1; 