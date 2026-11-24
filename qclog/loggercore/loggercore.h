#ifndef __loggercore_h
#define __loggercore_h

#include <QObject>
#include <QDir>
#include <qqml.h>
#include <QtSql/QSqlDatabase>

class LoggerCore : public QObject{
    Q_OBJECT

    Q_PROPERTY(QString name READ name)

    QML_ELEMENT
    QML_UNCREATABLE("LoggerCore needs proper initialization before exposing to QML")

public:
    LoggerCore(QString name, QObject * parent = 0);
    QString name(void) const;

private:
    const QString _name{};
    const QDir _datadir{};
    QSqlDatabase _db{};

    static QDir find_datadir(void);
};

#endif
