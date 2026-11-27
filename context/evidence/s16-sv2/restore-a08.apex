// SV-2 step 3: restore A08 (KnowledgeArticleId kA0jV000000WBwTSAW) and republish it.
final Id    TARGET_ARTICLE = 'kA0jV000000WBwTSAW';
final String TARGET_NUMBER = '000001011';
// Guard: A08 must be archived and must have no Online or Draft version.
List<Knowledge__kav> live = [SELECT Id FROM Knowledge__kav WHERE KnowledgeArticleId = :TARGET_ARTICLE
    AND PublishStatus IN ('Online','Draft') AND Language = 'en_US'];
List<Knowledge__kav> arch = [SELECT Id, ArticleNumber FROM Knowledge__kav WHERE KnowledgeArticleId = :TARGET_ARTICLE
    AND PublishStatus = 'Archived' AND Language = 'en_US' ALL ROWS];
if (!live.isEmpty() || arch.isEmpty() || arch[0].ArticleNumber != TARGET_NUMBER) {
    throw new IllegalArgumentException('GUARD FAILED: live=' + live + ' archived=' + arch);
}
// 1) Draft from the archived version (same content), 2) publish that draft.
String draftId = KbManagement.PublishingService.editArchivedArticle(TARGET_ARTICLE);
KbManagement.PublishingService.publishArticle(TARGET_ARTICLE, true);
System.debug('RESTORED draft=' + draftId + ' ' + [SELECT Id, ArticleNumber, PublishStatus, VersionNumber, Title
    FROM Knowledge__kav WHERE KnowledgeArticleId = :TARGET_ARTICLE AND PublishStatus = 'Online' AND Language = 'en_US']);
