import { Badge } from "@/components/ui/Badge";
import { STATUS_COLORS } from "@/lib/constants";

export function PostStatusBadge({ status }: { status: string }) {
  return (
    <Badge className={STATUS_COLORS[status] || "bg-gray-100 text-gray-700"}>
      {status.replace("_", " ")}
    </Badge>
  );
}
