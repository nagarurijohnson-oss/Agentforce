// SV-2 step 1: archive ONE synthetic Knowledge article, A08, immediately.
// Target: KnowledgeArticleId kA0jV000000WBwTSAW, Article 000001011,
//         "Athletic Scholarship – Required Documents". No record is deleted.
final Id    TARGET_ARTICLE = 'kA0jV000000WBwTSAW';
final String TARGET_NUMBER = '000001011';
// Guard: exactly one Online en_US version must exist for this article, with the expected number.
List<Knowledge__kav> online = [SELECT Id, ArticleNumber, Title FROM Knowledge__kav
    WHERE KnowledgeArticleId = :TARGET_ARTICLE AND PublishStatus = 'Online' AND Language = 'en_US'];
if (online.size() != 1 || online[0].ArticleNumber != TARGET_NUMBER) {
    throw new IllegalArgumentException('GUARD FAILED: expected 1 Online version of ' + TARGET_NUMBER + ', found ' + online);
}
// Single call, single article. null scheduled date = archive now.
KbManagement.PublishingService.archiveOnlineArticle(TARGET_ARTICLE, null);
System.debug('ARCHIVED ' + [SELECT Id, ArticleNumber, PublishStatus, VersionNumber FROM Knowledge__kav
    WHERE KnowledgeArticleId = :TARGET_ARTICLE AND PublishStatus = 'Archived' AND Language = 'en_US' ALL ROWS]);
