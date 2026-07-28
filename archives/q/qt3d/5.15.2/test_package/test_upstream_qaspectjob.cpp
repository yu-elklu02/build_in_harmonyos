/*
 * Upstream Qt3D 5.15.2 test: tests/auto/core/qaspectjob/tst_qaspectjob.cpp.
 * Kept in test_package so it is compiled against the packaged public API.
 * Only comments and the moc include name differ from the upstream source.
 */

#include <Qt3DCore/qaspectjob.h>
#include <QtTest/QtTest>

using namespace Qt3DCore;

class FakeAspectJob : public QAspectJob
{
public:
    void run() override {}
};

class tst_QAspectJob : public QObject
{
    Q_OBJECT

private Q_SLOTS:
    void shouldAddDependencies()
    {
        QAspectJobPtr job1(new FakeAspectJob);
        QAspectJobPtr job2(new FakeAspectJob);
        QAspectJobPtr job3(new FakeAspectJob);

        QVERIFY(job1->dependencies().isEmpty());
        QVERIFY(job2->dependencies().isEmpty());
        QVERIFY(job3->dependencies().isEmpty());

        job1->addDependency(job2);
        job1->addDependency(job3);

        QCOMPARE(job1->dependencies().size(), 2);
        QCOMPARE(job1->dependencies().at(0).lock(), job2);
        QCOMPARE(job1->dependencies().at(1).lock(), job3);
        QVERIFY(job2->dependencies().isEmpty());
        QVERIFY(job3->dependencies().isEmpty());
    }

    void shouldRemoveDependencies()
    {
        QAspectJobPtr job1(new FakeAspectJob);
        QAspectJobPtr job2(new FakeAspectJob);
        QAspectJobPtr job3(new FakeAspectJob);

        job1->addDependency(job2);
        job1->addDependency(job3);
        job1->removeDependency(job2);

        QCOMPARE(job1->dependencies().size(), 1);
        QCOMPARE(job1->dependencies().at(0).lock(), job3);
    }

    void shouldClearNullDependencies()
    {
        QAspectJobPtr job1(new FakeAspectJob);
        QAspectJobPtr job2(new FakeAspectJob);
        QAspectJobPtr job3(new FakeAspectJob);

        job1->addDependency(job2);
        job1->addDependency(job3);
        job2.clear();
        job1->removeDependency(QWeakPointer<QAspectJob>());

        QCOMPARE(job1->dependencies().size(), 1);
        QCOMPARE(job1->dependencies().at(0).lock(), job3);
    }
};

QTEST_MAIN(tst_QAspectJob)

#include "test_upstream_qaspectjob.moc"
