import * as functions from "firebase-functions";
import * as admin from "firebase-admin";
import { firestore } from "firebase-admin";
import DocumentSnapshot = firestore.DocumentSnapshot;
import axios from "axios";
import { timingSafeEqual } from "crypto";

admin.initializeApp(functions.config().firebase);

const COLLECTION_USERS = "users";
const COLLECTION_CONVERSATIONS = "conversations";
const COLLECTION_MESSAGES = "messages";

export const updateConversation = functions.region("europe-west2").firestore.document(`${COLLECTION_USERS}/{userId}/${COLLECTION_CONVERSATIONS}/{convId}/${COLLECTION_MESSAGES}/{messageId}`).onCreate(async (snapshot) => {
	const messageData = snapshot.data();
	const conversationRef = snapshot.ref.parent.parent;
	if (conversationRef) {
		const conversationDoc = await conversationRef.get();
		const conversationData = conversationDoc.data();

		let unreadCount = 0;
		if (conversationData && conversationData.unreadCount) {
			unreadCount = conversationData.unreadCount;
		}
		if (messageData.inbound) {
			unreadCount += 1;
		}

		return conversationRef.update({
			timestamp: messageData.timestamp,
			lastMessage: messageData.message,
			unreadCount
		});
	}
	return null;
});

/**
 * Resolves the user a provider webhook is for. The URL is /<userId>?token=<webhook_token>; the token is a per-user
 * secret stored on the user document, so knowing a user id alone isn't enough to inject messages.
 */
async function webhookUserId(request: functions.https.Request): Promise<string | null> {
	const userId = request.path.split("/").pop();
	const token = request.query.token;
	if (!userId || typeof token !== "string") {
		return null;
	}
	const userDoc = await admin.firestore().collection(COLLECTION_USERS).doc(userId).get();
	const expected = userDoc.get("webhook_token");
	if (typeof expected !== "string" || expected.length !== token.length ||
		!timingSafeEqual(Buffer.from(expected), Buffer.from(token))) {
		return null;
	}
	return userId;
}

export const sinchWebhook = functions.region("europe-west2").https.onRequest(async (request, response) => {
	const userId = await webhookUserId(request);
	if (!userId) {
		response.status(404).send("");
		return;
	}

	const conversationDocs = await admin.firestore().collection(COLLECTION_USERS).doc(userId).collection(COLLECTION_CONVERSATIONS).where("party", "==", request.body.from).get();
	let conversationDoc: DocumentSnapshot | null = null;
	if (conversationDocs.docs.length) {
		conversationDoc = conversationDocs.docs[0];
	} else {
		const newDocRef = await admin.firestore().collection(COLLECTION_USERS).doc(userId).collection(COLLECTION_CONVERSATIONS).add({ party: request.body.from });
		conversationDoc = await newDocRef.get();
	}

	await conversationDoc.ref.collection(COLLECTION_MESSAGES).add({
		message: request.body.body,
		timestamp: new Date(request.body.received_at),
		inbound: true
	});

	response.send("");
});

export const sinchSend = functions.region("europe-west2").firestore.document(`${COLLECTION_USERS}/{userId}/${COLLECTION_CONVERSATIONS}/{convId}/${COLLECTION_MESSAGES}/{messageId}`).onCreate(async (snapshot) => {
	const messageData = snapshot.data();
	if (!messageData.inbound) {
		const conversationDocRef = snapshot.ref.parent.parent;
		if (conversationDocRef) {
			const conversation = (await conversationDocRef.get()).data();
			const userDocRef = conversationDocRef.parent.parent;
			if (conversation && userDocRef) {
				const userDoc = (await userDocRef.get()).data();
				if (userDoc) {
					try {
						await axios.post(`https://eu.sms.api.sinch.com/xms/v1/${userDoc.sinch_account}/batches`, {
							to: [conversation.party],
							from: userDoc.number,
							body: messageData.message,
							type: "mt_text"
						}, {
							headers: {
								authorization: `Bearer ${userDoc.sinch_password}`
							}
						});
					} catch (e) {
						console.error(e);
					}
				}
			}
		}
	}
	return null;
});

export const simwoodWebhook = functions.region("europe-west2").https.onRequest(async (request, response) => {
	const userId = await webhookUserId(request);
	if (!userId) {
		response.status(404).send("");
		return;
	}

	const conversationDocs = await admin.firestore().collection(COLLECTION_USERS).doc(userId).collection(COLLECTION_CONVERSATIONS).where("party", "==", request.body.data.originator).get();
	let conversationDoc: DocumentSnapshot | null = null;
	if (conversationDocs.docs.length) {
		conversationDoc = conversationDocs.docs[0];
	} else {
		const newDocRef = await admin.firestore().collection(COLLECTION_USERS).doc(userId).collection(COLLECTION_CONVERSATIONS).add({ party: request.body.data.originator });
		conversationDoc = await newDocRef.get();
	}

	const messageDocRef = await conversationDoc.ref.collection(COLLECTION_MESSAGES).add({
		message: request.body.data.message,
		timestamp: new Date(request.body.data.time),
		inbound: true
	});

	response.send({
		message_id: messageDocRef.id,
		message: "Message stored successfully"
	});
});
