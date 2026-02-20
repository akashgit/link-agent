"use client";

import Link from "next/link";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Skeleton } from "@/components/ui/Skeleton";
import { usePosts } from "@/hooks/usePosts";
import { useCalendar } from "@/hooks/useCalendar";
import { STATUS_COLORS, PILLAR_COLORS } from "@/lib/constants";
import { formatDate } from "@/utils/formatDate";

export default function Dashboard() {
  const { data: posts, isLoading: postsLoading } = usePosts();
  const { data: calendar, isLoading: calLoading } = useCalendar();

  const recentPosts = posts?.slice(0, 5) || [];
  const upcomingEntries = calendar
    ?.filter((e) => new Date(e.scheduled_date) >= new Date())
    .slice(0, 5) || [];

  const stats = {
    total: posts?.length || 0,
    drafting: posts?.filter((p) => p.status === "drafting").length || 0,
    approved: posts?.filter((p) => p.status === "approved").length || 0,
    published: posts?.filter((p) => p.status === "published").length || 0,
  };

  return (
    <div className="space-y-8">
      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "Total Posts", value: stats.total, color: "text-gray-900" },
          { label: "Drafting", value: stats.drafting, color: "text-yellow-600" },
          { label: "Approved", value: stats.approved, color: "text-green-600" },
          { label: "Published", value: stats.published, color: "text-blue-600" },
        ].map((stat) => (
          <Card key={stat.label}>
            <p className="text-sm text-gray-500">{stat.label}</p>
            {postsLoading ? (
              <Skeleton className="h-8 w-16 mt-1" />
            ) : (
              <p className={`text-2xl font-bold ${stat.color}`}>{stat.value}</p>
            )}
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Recent Posts */}
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold">Recent Posts</h3>
            <Link href="/posts"><Button variant="ghost" size="sm">View All</Button></Link>
          </div>
          {postsLoading ? (
            <div className="space-y-3">{[...Array(3)].map((_, i) => <Skeleton key={i} className="h-12 w-full" />)}</div>
          ) : recentPosts.length === 0 ? (
            <p className="text-sm text-gray-500">No posts yet. <Link href="/create" className="text-blue-600 hover:underline">Create your first post</Link></p>
          ) : (
            <div className="space-y-3">
              {recentPosts.map((post) => (
                <Link key={post.id} href={`/posts/${post.id}`} className="flex items-center justify-between p-2 rounded hover:bg-gray-50">
                  <div className="min-w-0">
                    <p className="text-sm font-medium truncate">{post.title}</p>
                    <Badge className={`${PILLAR_COLORS[post.content_pillar]} text-[10px] mt-1`}>
                      {post.content_pillar.replace("_", " ")}
                    </Badge>
                  </div>
                  <Badge className={STATUS_COLORS[post.status]}>{post.status.replace("_", " ")}</Badge>
                </Link>
              ))}
            </div>
          )}
        </Card>

        {/* Upcoming Calendar */}
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold">Upcoming Content</h3>
            <Link href="/calendar"><Button variant="ghost" size="sm">View Calendar</Button></Link>
          </div>
          {calLoading ? (
            <div className="space-y-3">{[...Array(3)].map((_, i) => <Skeleton key={i} className="h-12 w-full" />)}</div>
          ) : upcomingEntries.length === 0 ? (
            <p className="text-sm text-gray-500">No upcoming content planned.</p>
          ) : (
            <div className="space-y-3">
              {upcomingEntries.map((entry) => (
                <div key={entry.id} className="flex items-center justify-between p-2 rounded hover:bg-gray-50">
                  <div className="min-w-0">
                    <p className="text-sm font-medium truncate">{entry.topic}</p>
                    <p className="text-xs text-gray-500">{formatDate(entry.scheduled_date)}</p>
                  </div>
                  <Badge className={PILLAR_COLORS[entry.content_pillar]}>{entry.post_format.replace("_", " ")}</Badge>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>

      {/* Quick action */}
      <div className="text-center">
        <Link href="/create">
          <Button size="lg">Create New Post</Button>
        </Link>
      </div>
    </div>
  );
}
